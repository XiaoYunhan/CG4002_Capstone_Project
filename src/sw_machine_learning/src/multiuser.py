from threading import Thread, Lock
from queue import Queue
from joblib import load
import logging

from sklearn.svm import SVC

from sklearn.preprocessing import MinMaxScaler

#from src.models.mlp import *
from sklearn.ensemble import RandomForestRegressor
from ..comm_external.multiple_server import *
from ..hardware_fpga.fpga import FinnDriver

IDLE_FRAME = "-1/-1/-1/-1/-1/-1"
IGNORE_FRAME = 10
START = 100
END = 100

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class MultiUser():
    def __init__(self, queue, use_fpga):
        #self.model = load_model(os.getcwd() + "/models/")
        #self.model.eval()
        self.use_fpga = use_fpga
        if use_fpga:
            self.driver = FinnDriver()
        else:
            self.model = load('models/rbf.joblib')
        self.rf = load('models/rf.joblib')
        self.lock_move = Lock()
        self.lock_pos = Lock()
        self.queue = queue
        self.q_pkt = [(-1,1),(-1,2),(-1,3)]

    def init_server(self, IP_ADDR, PRT, GRP, ID):
        server = Server(IP_ADDR, PRT, GRP)
        server.id = ID
        server.pos = ID 
        server.start()
        print("Server started at", IP_ADDR, PRT)
        return server

    # def load_model(self, PATH):
    #     model = mlp()
    #     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    #     model.load_state_dict(torch.load(PATH + "mlp_1510_0451.pt", map_location=device))
    #     print("Model Loaded")
    #     return model


    # def eval_model(self, model, frame):
    #     Y_test_pred = model(frame)
    #     Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
    #     _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
    #     return Y_pred_tags.cpu().numpy()

    def process_data(self, server, use_fpga):  
        prev_msg = ""
        idle_count = 0
        MOVE_TIMEOUT = 0
        POS_TIMEOUT = 0
        move_frame = []
        pos_frame = []
        start = False
        start_count = START 
        end_count = END
        out = -1
        while True:
            if not start and start_count == 0:
                start = True
                self.queue.put("Start")
            if start and end_count == 0:
                self.q_pkt[server.id - 1] = (8,server.pos)
                self.queue.put(self.q_pkt)
                break
            move_data = '/'.join(server.raw_data.split("/")[1:7])
            pos_data = '/'.join(server.raw_data.split("/")[7:13])
            if prev_msg != move_data:
                if MOVE_TIMEOUT > 0:
                    MOVE_TIMEOUT = MOVE_TIMEOUT - 1
                if POS_TIMEOUT > 0:
                    POS_TIMEOUT = POS_TIMEOUT - 1
                if move_data == IDLE_FRAME:
                    if not start:
                        start_count = start_count - 1
                        continue
                    idle_count = idle_count + 1
                    end_count = end_count - 1
                    if idle_count >= IGNORE_FRAME:
                        idle_count = 0
                        move_frame.clear()
                else:
                    if not start:
                        start_count = START
                        continue
                    prev_msg = move_data
                    idle_count = 0
                    end_count = END
                    move_frame = move_frame + move_data.split("/")
                    if len(move_frame) == 60:
                        #df = torch.from_numpy(np.array(MinMaxScaler().fit_transform([move_frame]))).float()
                        self.lock_move.acquire()
                        try:
                        #out = eval_model(self.model, df)[0]
                            if self.use_fpga:
                                move_frame = np.array(move_frame, dtype="float32")
                                out = driver.predict(move_frame)
                            else:
                                out = self.model.predict([move_frame])[0]
                            msg = "Predicted Dance Move: " + ACTIONS[out]
                            logging.info(msg)
                            self.q_pkt[server.id - 1] = (out, server.pos) 
                            self.queue.put(self.q_pkt)
                            self.q_pkt[server.id - 1] = (-1, server.pos)
                        finally:
                            self.lock_move.release()
                        del move_frame[0:12]
                        MOVE_TIMEOUT = 12
                
                if pos_data == IDLE_FRAME or POS_TIMEOUT > 0:
                    pos_frame.clear()
                else:
                    pos_frame = pos_frame + pos_data.split("/")
                    if len(pos_data) == 30:
                        self.lock_pos.acquire()
                        try:
                            pos_out = np.round(np.clip(self.rf.predict([pos_frame]), 0, 1)).astype(bool)[0]
                            if pos_out:
                                logging.info("Movement RIGHT")
                                if server.pos < 3:
                                    server.pos = server.pos + 1
                            else:
                                logging.info("Movement LEFT")
                                if server.pos > 1:
                                    server.pos =  server.pos - 1
                            pos_frame.clear()
                            self.q_pkt[server.id - 1] = (-1, server.pos) 
                            self.queue.put(self.q_pkt)
                            POS_TIMEOUT = 10
                        finally:
                            self.lock_pos.release()        
from threading import Thread, Lock
from queue import Queue
from joblib import load
import time
from time import sleep
import logging

    

from sklearn.preprocessing import MinMaxScaler

#from src.models.mlp import *
from sklearn.ensemble import RandomForestRegressor
from comm_external.multiple_server import *
from fpga import FinnDriver
from src.features import convert_raw



logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class MultiUser():
    def __init__(self, q_users, args):
        #self.model = load_model(os.getcwd() + "/models/")
        #self.model.eval()
        logging.info("Multi User has been init")
        self.use_fpga = args.use_fpga
        self.use_feat = args.use_feat
        self.is_eval = args.eval
        if self.use_fpga:
            #pass
            self.driver = FinnDriver()
        elif self.use_feat:
            self.scaler = load('models/feat_scaler.joblib')
            self.model = load('models/rbf_feat.joblib')
        else:
            self.model = load('models/rbf0511.joblib')
        self.rf = load('models/rf.joblib')
        self.lock = Lock()
        self.q_users = q_users
        if self.is_eval:
            self.q_eval = q_eval
        #self.q_pkt = [-1,(-1,1),(-1,2),(-1,3)]

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

    def process_data(self, server):
        q_pkt = [-1,-1,server.id]
        IDLE_FRAME = "-1/-1/-1/-1/-1/-1"
        IGNORE_FRAME = 10
        START_TIME = 3
        END_TIME = 8 
        prev_msg = ""
        idle_count = 0
        MOVE_TIMEOUT = 0.2
        POS_TIMEOUT = 2
        move_frame_feat = [[],[],[],[],[],[]]
        move_frame = []
        FRAME_SIZE = 60
        if self.use_feat:
            FRAME_SIZE = 72
        pos_frame = []
        start = False
        start_count = time.time() 
        end_count = 0
        CMD = 0
        MOVE = 1
        out = -1
        
        while True:
            # if self.is_eval:
                # try:
                    # data = q_eval.get()
                    # pos = data.split(" ")
                    # q_pkt[1] = (-1, pos[0])
                    # q_pkt[2] = (-1, pos[1])
                    # q_pkt[3] = (-1, pos[2])
                    # logging.info("Reset to " + data)
                # except:
                    # pass
            if not start and time.time() - start_count > START_TIME:
                start = True
                end_count = time.time()
                q_pkt[CMD] = 2
                logging.info("USER-" + str(server.id) + " has started run")
                self.q_users.put(q_pkt)
                sleep(1e-12)
            if start and time.time() - end_count > END_TIME:
               q_pkt[CMD] = 3
               self.q_users.put(q_pkt)
               logging.info("USER-" + str(server.id) + " has ended run")
               break
            move_data = '/'.join(server.raw_data.split("/")[1:7])
            pos_data = '/'.join(server.raw_data.split("/")[7:13]).rstrip()
            #logging.info("MV: " + move_data + " POS: " + pos_data)
            if prev_msg != move_data and len(move_data) > 0 and len(pos_data) > 0:
                if move_data == IDLE_FRAME:
                    idle_count = idle_count + 1
                    if idle_count >= IGNORE_FRAME:
                        idle_count = 0
                        move_frame.clear()
                if move_data != IDLE_FRAME and pos_data == IDLE_FRAME:
                    #logging.info("Wrist is moving, not Feet")
                    if start:
                        prev_msg = move_data
                        idle_count = 0
                        if self.use_feat:
                            tmp = move_data.split("/")
                            #logging.info(tmp)
                            for i in range(6):
                                #logging.info(move_frame_feat)
                                move_frame_feat[i].append(tmp[i])   
                        else:
                            move_frame = move_frame + move_data.split("/")
                        #logging.info("Length of move frame is " + str(sum(len(row) for row in move_frame)))
                        if sum(len(row) for row in move_frame_feat) == FRAME_SIZE:
                        #if len(move_frame) == FRAME_SIZE:
                            #df = torch.from_numpy(np.array(MinMaxScaler().transform([move_frame]))).float()
                            self.lock.acquire()
                            try:
                            #out = eval_model(self.model, df)[0]
                                if self.use_fpga:
                                    #pass
                                    move_frame_np = np.array(move_frame, dtype="float64")
                                    out = self.driver.predict([move_frame_np])
                                elif self.use_feat: 
                                    move_frame_np = np.array(move_frame_feat, dtype="float64")
                                    converted = convert_raw(move_frame_np)
                                    coverted = self.scaler.transform([converted])
                                    out = self.model.predict([converted])[0]
                                else:
                                    out = self.model.predict([move_frame])[0]
                                msg = str(server.id) + "-: Predicted Dance Move: " + ACTIONS[out]
                                logging.info(msg)
                                q_pkt[MOVE] = out
                                q_pkt[CMD] = 0
                                #logging.info(q_pkt)
                                self.q_users.put(q_pkt)
                                sleep(1e-9)
                                q_pkt[MOVE] = -1
                            finally:
                                self.lock.release()
                            #del move_frame[0:18]
                            move_frame.clear()
                            sleep(MOVE_TIMEOUT)
                        end_count = time.time()
                    else:
                        start_count = time.time()
                        continue
                if pos_data == IDLE_FRAME:
                    pos_frame.clear()
                if move_data != IDLE_FRAME and pos_data != IDLE_FRAME:
                    idle_count = 0
                    if start:
                        pos_frame = pos_frame + pos_data.split("/")
                        #logging.info("Pos_frame is ")
                        #logging.info(pos_frame)
                        if len(pos_frame) == 30:
                            #logging.info("Position change detected")
                            self.lock.acquire()
                            try:
                                pos_out = np.round(np.clip(self.rf.predict([pos_frame]), 0, 1)).astype(bool)[0]
                                if pos_out:
                                    logging.info(str(server.id) + "-: Movement RIGHT")
                                    q_pkt[MOVE] = 1
                                    # if server.pos < 3:
                                        # server.pos = server.pos + 1
                                else:
                                    logging.info(str(server.id) + "-: Movement LEFT")
                                    q_pkt[MOVE] = 0
                                    # if server.pos > 1:
                                        # server.pos =  server.pos - 1
                                pos_frame.clear()
                                q_pkt[CMD] = 1
                                #logging.info(q_pkt)
                                self.q_users.put(q_pkt)
                                sleep(1e-9)
                            finally:
                                self.lock.release()
                                sleep(POS_TIMEOUT)
                        end_count = time.time()
                    else:
                        start_count = time.time()

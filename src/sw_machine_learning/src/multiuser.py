from threading import Thread, Lock
from queue import Queue
from joblib import load
import time
from time import sleep
import logging

    

#from sklearn.preprocessing import MinMaxScaler

#from src.models.mlp import *
from sklearn.ensemble import RandomForestRegressor
from comm_external.multiple_server import *
from fpga import FinnDriver
from src.features import convert_raw, convert_raw_pos



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
            self.scaler = load('models/feat_all_scaler.joblib')
            self.driver = FinnDriver()
        elif self.use_feat:
            self.scaler = load('models/feat_all_scaler.joblib')
            self.model = load('models/skl_mlp_feat.joblib')
        else:
            self.model = load('models/rbf0511.joblib')
        self.rf = load('models/rbf_pos_feat.joblib')
        self.pos_scaler = load('models/pos_feat_scaler.joblib')
        self.lock = Lock()
        self.q_users = q_users
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
        END_TIME = 10 
        prev_move = ""
        prev_pos = ""
        idle_count = 0
        MOVE_TIMEOUT = 0.2
        POS_TIMEOUT = 2
        move_frame_feat = [[],[],[],[],[],[]]
        move_frame = []
        FRAME_SIZE = 60
        if self.use_feat or self.use_fpga:
            FRAME_SIZE = 72
        pos_frame = [[],[],[],[],[],[]]
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
            if prev_move != move_data and len(move_data) > 0 and len(pos_data) > 0:
                #logging.info(server.raw_data)
                if move_data == IDLE_FRAME:
                    idle_count = idle_count + 1
                    if idle_count >= IGNORE_FRAME:
                        idle_count = 0
                        move_frame.clear()
                        move_frame_feat = [[],[],[],[],[],[]]
                if move_data != IDLE_FRAME and pos_data == IDLE_FRAME:
                    #logging.info("Wrist is moving, not Feet")
                    prev_move = move_data
                    idle_count = 0
                    if start:
                        if self.use_feat or self.use_fpga:
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
                                    move_frame_np = np.array(move_frame_feat, dtype="float64")
                                    converted = convert_raw(move_frame_np)
                                    #converted_trf = self.scaler.transform([converted])
                                    out = self.driver.predict([converted])
                                elif self.use_feat: 
                                    move_frame_np = np.array(move_frame_feat, dtype="float64")
                                    converted = convert_raw(move_frame_np)
                                    converted_trf = self.scaler.transform([converted])
                                    #out = self.model.predict(converted_trf)[0]
                                    out_prob = self.model.predict_log_proba(converted_trf)
                                    adj_matrix = [0.10,1.25,2,1.1,1.8,1.3,0.8,1.1]
                                    out = np.argmax(np.asarray([a*b for a,b in zip(out_prob, adj_matrix)]))
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
                            except Exception as e:
                                print(e)
                            finally:
                                self.lock.release()
                            #del move_frame[0:18]
                            move_frame.clear()
                            move_frame_feat = [[],[],[],[],[],[]]
                            sleep(MOVE_TIMEOUT)
                        end_count = time.time()
                        continue
                    else:
                        start_count = time.time()
                        continue
                if pos_data == IDLE_FRAME:
                    pos_frame.clear()
                    pos_frame = [[],[],[],[],[],[]]
                if prev_pos != pos_data and pos_data != IDLE_FRAME:
                    idle_count = 0
                    prev_pos = pos_data
                    if start:
                        pos_tmp = pos_data.split("/")
                        assert len(pos_tmp) == 6
                        for i in range(6):
                            #logging.info(pos_frame)
                            pos_frame[i].append(pos_tmp[i]) 
                        #pos_frame = pos_frame + pos_data.split("/")
                        #logging.info("Pos_frame is ")
                        #logging.info(pos_frame)
                        if sum(len(row) for row in pos_frame) == 30:
                            #logging.info("Position change detected")
                            self.lock.acquire()
                            try:
                                pos_frame_np = np.array(pos_frame, dtype="float64")
                                pos_converted = convert_raw_pos(pos_frame_np)
                                pos_converted = self.pos_scaler.transform([pos_converted])
                                pos_out = self.rf.predict(pos_converted)[0]
                                #pos_out = np.round(np.clip(self.rf.predict([pos_frame]), 0, 1)).astype(bool)[0]
                                if pos_out == 0:
                                    logging.info(str(server.id) + "-: Movement RIGHT")
                                    # if server.pos < 3:
                                        # server.pos = server.pos + 1
                                else:
                                    logging.info(str(server.id) + "-: Movement LEFT")
                                    # if server.pos > 1:
                                        # server.pos =  server.pos - 1
                                pos_frame.clear()
                                pos_frame = [[],[],[],[],[],[]]
                                q_pkt[MOVE] = pos_out
                                q_pkt[CMD] = 1
                                #logging.info(q_pkt)
                                self.q_users.put(q_pkt)
                                sleep(1e-9)
                            except Exception as e:
                                print(e)
                            finally:
                                self.lock.release()
                                sleep(POS_TIMEOUT)
                        end_count = time.time()
                    else:
                        start_count = time.time()

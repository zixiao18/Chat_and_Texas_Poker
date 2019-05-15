


"""
Created on Tue Jul 22 00:47:05 2014
@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import threading
from texas_main_game import *

S_ALLIN = 'allin'
FOLD = 'fold'

#### change


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.game_players_g = []

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name + '.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "ok"}))
                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

    # ==============================================================================
    # main command switchboard
    # ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))


                    ####change
                    game_player_1 = Players(from_name)
                    game_player_2 = Players(to_name)
                    self.game_players_g.append(game_player_1)
                    self.game_players_g.append(game_player_2)
                    print('players established')






                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)






                ######



                g_th = threading.Thread(target=game_start, args=(game_player_1, game_player_2))
                #game_start(game_player_1, game_player_2)
                #g_th.deamon = True
                g_th.start()


                print('game started')

                msg = json.loads(msg)

                time.sleep(CHAT_WAIT * 2)
                for other in self.game_players_g:

                    while len(other.to_recieve) > 0:
                        msg['message'] = other.to_recieve.pop(0)
                        # other.to_recieve = ''
                        msg['from'] = '[server] '
                        said2 = text_proc(msg["message"], from_name)

                        # print('the action is recieved by the server and passed to the texas program',people.action)
                        # ---- end of your code --- #

                        for g in the_guys:
                            if g == other.name:
                                to_sock = self.logged_name2sock[g]
                                # IMPLEMENTATION
                                # ---- start your code ---- #
                                # add indices to people you send, so that what you send is also in their chat history
                                self.indices[g].add_msg_and_index(said2)
                                # send the message, turn the dictionary into a string
                                mysend(to_sock, json.dumps(
                                    {"action": "exchange", "from": msg["from"], "message": msg["message"]}))








            elif msg["action"] == "connect_g":
                print("the message that i receive is", msg)
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect_g", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect_g", "status": "success"})



                    game_player_1 = Players(from_name)
                    game_player_2 = Players(to_name)
                    self.game_players_g.append(game_player_1)
                    self.game_players_g.append(game_player_2)
                    print('players established')




                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect_g", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect_g", "status": "no-user"})



                mysend(from_sock, msg)
                msg = json.loads(msg)
                # change

                # player1, player2, pot = game_start(from_name, to_name, from_sock, to_sock)
                # player1, player2, pot = \

                g_th = threading.Thread(target=game_start, args=(game_player_1, game_player_2))
                #game_start(game_player_1, game_player_2)
                #g_th.deamon = True
                g_th.start()


                print('game started')

                time.sleep(CHAT_WAIT*2)
                for other in self.game_players_g:

                    while len(other.to_recieve) > 0:
                        msg['message'] = other.to_recieve.pop(0)
                        # other.to_recieve = ''
                        msg['from'] = '[server] '

                        # print('the action is recieved by the server and passed to the texas program',people.action)
                        # ---- end of your code --- #

                        for g in the_guys:
                            if g == other.name:
                                to_sock = self.logged_name2sock[g]
                                # IMPLEMENTATION
                                # ---- start your code ---- #
                                # add indices to people you send, so that what you send is also in their chat history
                                self.indices[g].add_msg_and_index(said2)
                                # send the message, turn the dictionary into a string
                                mysend(to_sock, json.dumps(
                                    {"action": "exchange", "from": msg["from"], "message": msg["message"]}))



               # return player1, player2, pot


            # ==============================================================================
            # handle messeage exchange: IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                the_guys = self.group.list_me(from_name)

                # format the message: at what time, from whom, what is the message
                said2 = text_proc(msg["message"], from_name)

                #self.indices is a dictionary: name, message and index
                #add index in your chat history
                self.indices[from_name].add_msg_and_index(said2)




                #####change
                for people in self.game_players_g:
                    if people.name != from_name:
                        continue
                    else:
                        people.action = msg['message']
                        time.sleep(CHAT_WAIT)
                        for other in self.game_players_g:

                            while len(other.to_recieve) > 0:
                                msg['message'] = other.to_recieve.pop(0)
                               # other.to_recieve = ''
                                msg['from'] = '[server] '

                        # print('the action is recieved by the server and passed to the texas program',people.action)
                # ---- end of your code --- #

                                for g in the_guys:
                                    if g == other.name:
                                        to_sock = self.logged_name2sock[g]
                                        # IMPLEMENTATION
                                        # ---- start your code ---- #
                                        #add indices to people you send, so that what you send is also in their chat history
                                        self.indices[g].add_msg_and_index(said2)
                                        #send the message, turn the dictionary into a string
                                        mysend(to_sock, json.dumps({"action": "exchange", "from": msg["from"], "message": msg["message"]}))

                    # ---- end of your code --- #




            elif msg["action"] == "exchange_g":
                from_name = self.logged_sock2name[from_sock]
                print(from_name)
                print("this is a line from server")
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                the_guys = self.group.list_me(from_name)
                print(the_guys)
                said2 = text_proc(msg["message"], from_name)
                print("GUYS Found")



                for people in self.game_players_g:
                    if people.name != from_name:
                        continue
                    else:
                        people.action = msg['message']
                        time.sleep(CHAT_WAIT * 2)
                        for other in self.game_players_g:
                            if other != people:
                                msg['message'] = other.to_recieve
                                other.to_recieve = ''
                                msg['from'] = 'server'


                        print('the action is recieved by the server and passed to the texas program',people.action)


                #self.indices[from_name].add_msg_and_index(said2)

                # ---- end of your code --- #

                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    # IMPLEMENTATION
                    # ---- start your code ---- #
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action": "exchange_g", "from": msg["from"], "message": msg["message"]}))



                    # ---- end of your code --- #


            # ==============================================================================
            # the "from" guy has had enough (talking to "to")!
            # ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "message": "everyone left, you are alone"}))
            # ==============================================================================
            #                 listing available peers: IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                # msg = "...needs to use self.group functions to work"

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
            # ==============================================================================
            #             retrieve a sonnet : IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                # poem = "...needs to use self.sonnet functions to work"
                print('here:\n', poem)

                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
            # ==============================================================================
            #                 time
            # ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
            # ==============================================================================
            #                 search: : IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                # search_rslt = "needs to use self.indices search to work"
                search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
                print('server side search: ' + search_rslt)

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))

        # ==============================================================================
        #                 the "from" guy really, really has had enough
        # ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

    # ==============================================================================
    # main loop, loops *forever*
    # ==============================================================================
    def run(self):
        print('starting server...')
        while (1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)



def main():
    server = Server()
    server.run()

if __name__ == '__main__':
    main()










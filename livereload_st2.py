import sublime, sublime_plugin,threading,json
from websocket import WebSocketServer

class LiveReload(threading.Thread):

    def __init__(self):
      global  LivereloadFactory
      threading.Thread.__init__(self)
      LivereloadFactory = WSLiveReload()

    def run(self):
      global  LivereloadFactory
      LivereloadFactory.start_server()

class WSLiveReload(WebSocketServer):

    clients = []
    settings = sublime.load_settings('LiveReload.sublime-settings')

    def __init__  (self):
      super(WSLiveReload, self).__init__()
      
      self.listen_host = self.settings.get('host')
      self.listen_port = self.settings.get('port')
      
    def new_client(self):
        self.clients = [self]
        self.log("Browser connected.")
        self.send("!!ver:"+str(self.settings.get('version')))
        while True:
          self.pool()
    
    def pool(self): 
      frames, closed = self.recv_frames()
      if closed:
        self.send_close()
        self.clist.remove(self)
        self.log("Browser disconnected.")
        raise self.EClose(closed)
      else:
        self.parse(frames[0])

    def send(self, string):
      for cl in self.clients:
        cl.send_frames([string])
    
    def parse(self, string):
      self.log("Browser URL: "+string)
    
    def log(self,string):
      sublime.status_message(string)

    def update(self, file):
      
      data = json.dumps(["refresh", {
          "path": file,
          "apply_js_live": self.settings.get('apply_js_live'),
          "apply_css_live": self.settings.get('apply_css_live'),
          "apply_images_live": self.settings.get('apply_images_live')
      }])
      sublime.set_timeout(lambda: self.send(data), int(self.settings.get('delay_ms')))    
        

class LiveReloadChange(sublime_plugin.EventListener):
    def __init__  (self):
      LiveReload().start()

    def __del__(self):
      global  LivereloadFactory
      LivereloadFactory.stop_server()

    def on_post_save(self, view):
      global  LivereloadFactory
      LivereloadFactory.update(view.file_name())

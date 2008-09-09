from __future__ import with_statement

import os
import urllib
import webbrowser
import pickle
import cherrypy

from gh600 import GH600, Utilities, Waypoint
from templates import Template

class HTMLTemplate(Template):
    def __init__(self, file, **kwargs):
        highlight = file.split("/")[0]
        master = Template.from_file(Utilities.getAppPrefix('gui', 'tpl', 'global', 'master.html'))
        content = open(Utilities.getAppPrefix('gui', 'tpl', file)).read()
        merged = master.render(content=content, highlight=highlight)
        super(HTMLTemplate, self).__init__(merged, **kwargs)
        
    
class Root:
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/waypoints')

    @cherrypy.expose
    def exit(self):
        raise SystemExit(0)


class Waypoints:
    def getWaypointLibrary(self):
        if not os.path.exists('waypoint_library'):
            pickle.dump([], open("waypoint_library", 'wb'))
            return []
        return pickle.load(open("waypoint_library"))
    
    def saveWaypointLibrary(self, waypoints):
        pickle.dump(waypoints, open("waypoint_library", 'wb'))

    def getWaypointsFromGh(self, force = False):
        if not "waypoints" in cherrypy.session or force:
            cherrypy.session['waypoints'] = gh.getWaypoints()
        return cherrypy.session.get('waypoints')
    
    def saveWaypointsToGh(self, waypoints):
        gh.setWaypoints(waypoints)
        self.getWaypointsFromGh(True)
        pass
    
    @cherrypy.expose
    def index(self):
        t = HTMLTemplate('waypoints/index.html')
        waypointLibrary = self.getWaypointLibrary()
        remoteWaypoints = self.getWaypointsFromGh()
        return t.render(waypointLibrary = waypointLibrary, remoteWaypoints = remoteWaypoints)
    
    @cherrypy.expose
    def add(self):
        t = HTMLTemplate('waypoints/add.html')
        return t.render(types = Waypoint.TYPES)
    
    @cherrypy.expose
    def doAdd(self, latitude, longitude, altitude, title, type = 0, operation = "save"):                
        w = Waypoint(latitude, longitude, altitude, title, type)
        waypoints = self.getWaypointLibrary()
        waypoints.append(w)
        self.saveWaypointLibrary(waypoints)

        if operation != "save":
            self.saveWaypointsToGh([w])
        raise cherrypy.HTTPRedirect('/waypoints')
        
    @cherrypy.expose
    def edit(self, id = 0):    
        waypoint = self.getWaypointLibrary()[int(id)]
        waypoint.id = id
        
        template = HTMLTemplate('waypoints/edit.html')
        return template.render(waypoint = waypoint, waypointTypes = Waypoint.TYPES)
    
    @cherrypy.expose
    def doEdit(self, id, latitude, longitude, altitude, title, type, operation = "save"):    
        waypoints = self.getWaypointLibrary()
        del waypoints[int(id)]
        w = Waypoint(latitude, longitude, altitude, title, int(type))
        waypoints.insert(int(id), w)
        self.saveWaypointLibrary(waypoints)
        
        if operation != "save":
            self.saveWaypointsToGh([w])
        raise cherrypy.HTTPRedirect('/waypoints')
        
    @cherrypy.expose
    def doDelete(self, toBeDeleted):
        waypoints = self.getWaypointLibrary()
        #if only one waypoint is to be deleted post is string, otherwise list
        if isinstance(toBeDeleted, str):
            del waypoints[int(toBeDeleted)]
        else:
            toBeDeleted.reverse()
            for id in toBeDeleted:
                del waypoints[int(id)]
        
        self.saveWaypointLibrary(waypoints)    
        raise cherrypy.HTTPRedirect('/waypoints')
    
    @cherrypy.expose
    def doDeleteAll(self):
        gh.formatWaypoints()
        self.getWaypointsFromGh(True)
        raise cherrypy.HTTPRedirect('/waypoints')
    
    @cherrypy.expose
    def doCopyToGh(self, toBeCopied):
        waypoints = self.getWaypointLibrary()
        
        copyMe = []
        if isinstance(toBeCopied, str):
            copyMe.append(waypoints[int(toBeCopied)])
        else:
            for id in toBeCopied:
                copyMe.append(waypoints[int(id)])

        self.saveWaypointsToGh(copyMe)
        raise cherrypy.HTTPRedirect('/waypoints')

    @cherrypy.expose
    def doCopyToLibrary(self, toBeCopied):
        waypoints = self.getWaypointLibrary()
        remoteWaypoints = self.getWaypointsFromGh()
        
        if isinstance(toBeCopied, str):
            waypoints.append(remoteWaypoints[int(toBeCopied)])
        else:
            for id in toBeCopied:
                waypoints.append(remoteWaypoints[int(id)])
        self.saveWaypointLibrary(waypoints)
        raise cherrypy.HTTPRedirect('/waypoints')
    
    @cherrypy.expose
    def getWaypointAltitude(self, latitude = 0, longitude = 0):
        try:
            f = urllib.urlopen("http://ws.geonames.org/srtm3?lat=%s&lng=%s" % (str(latitude), str(longitude)))
            return f.read()
        except:
            return "0"
        
class Settings:
    @cherrypy.expose
    def index(self):
        gh615Config = {}
        for section in gh.config.sections():
            if not section in gh615Config:
                gh615Config[section] = {}
            for item, value in gh.config.items(section):
                gh615Config[section][item] = value
        
        with open('GH600.log') as f:
            log = f.read()
            
        template = HTMLTemplate('settings/index.html')
        return template.render(gh615Config = gh615Config, log = log)    
    
    @cherrypy.expose
    def doUpdate(self, **kwargs):
        for arg in kwargs:
            (section, option) = arg.split('/')
            value = kwargs[arg]
            gh.config.set(section, option, value)
        
        with open('config.ini', 'w') as f:
            gh.config.write(f)
        raise cherrypy.HTTPRedirect('/settings')

class Error:
    @cherrypy.expose
    def index(self):
        template = HTMLTemplate('global/error.html')
        return template.render()


gh = GH600()
if gh.testConnectivity():
    #SITEMAP
    root = Root()
    root.waypoints = Waypoints()
    root.settings = Settings()
else:
    root = Error()
cherrypy.tree.mount(root, config="gui/app.conf")

def launch_browser():
    print "Gui running"
    print "Your browser will now be pointed to %s" % cherrypy.server.base()
    print "When you are done, just close this window"
    webbrowser.open(cherrypy.server.base())
cherrypy.engine.subscribe('start', launch_browser)

if __name__ == '__main__':
    cherrypy.quickstart(config=Utilities.getAppPrefix('gui', 'cherrypy.conf'))
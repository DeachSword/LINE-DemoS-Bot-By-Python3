# -*- coding: utf-8 -*-

import json, time, base64, hashlib

class TimelineObs():

    def updateProfileCover(self, path):
        hstr = 'DearSakura_%s' % int(time.time()*1000)
        objid = hashlib.md5(hstr.encode()).hexdigest()
        objId = self.uploadObjHome(path, type='image', objId=objid)
        home = self.updateProfileCoverById(objId)
        return objId

    def updateImageToAlbum(self, mid, albumId, path):
        pass
        #privie
    
    def uploadObjHome(self, path, type='image', objId=None):
        if type not in ['image','video','audio']:
            raise Exception('Invalid type value')
        if type == 'image':
            contentType = 'image/jpeg'
        elif type == 'video':
            contentType = 'video/mp4'
        elif type == 'audio':
            contentType = 'audio/mp3'
        if not objId:
            hstr = 'DearSakura_%s' % int(time.time()*1000)
            objid = hashlib.md5(hstr.encode()).hexdigest()
        file = open(path, 'rb').read()
        params = {
            'name': '%s' % str(time.time()*1000),
            'userid': '%s' % self.profile.mid,
            'oid': '%s' % str(objId),
            'type': type,
            'ver': '1.0' #2.0 :p
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': contentType,
            'Content-Length': str(len(file)),
            'x-obs-params': self.genOBSParams(params,'b64') #base64 encode
        })
        r = self.server.postContent('https://obs-tw.line-apps.com/myhome/c/upload.nhn', headers=hr, data=file)

        if r.status_code != 201:
            raise Exception(f"Upload object home failure. Receive statue code: {r.status_code}")
        return objId
        
    def uploadObjTalk(self, path=None, type='image', objId=None, to=None):
        if type not in ['image','gif','video','audio','file']:
            raise Exception('Invalid type value')
        headers=None
        files = {'file': open(path, 'rb')}
        url = 'https://obs.line-apps.com/talk/m/upload.nhn'
        if type == 'image' or type == 'video' or type == 'audio' or type == 'file':
            data = {'params': self.genOBSParams({'oid': objId,'size': len(open(path, 'rb').read()),'type': type})}
        elif type == 'gif':
            url = 'https://obs.line-apps.com/r/talk/m/reqseq'
            params = {
                'type': 'image',
                'ver': '2.0',
                'name': files['file'].name,
                'oid': 'reqseq',
                'reqseq': '%s' % str(self.revision),
                'tomid': '%s' % str(to),
                'cat': 'original'
            }
            files = None
            data = open(path, 'rb').read()
            headers = self.server.additionalHeaders(self.server.Headers, {
                'content-type': 'image/gif',
                'Content-Length': str(len(data)),
                'x-obs-params': self.genOBSParams(params,'b64'), #base64 encode
                'X-Line-Access': self.acquireEncryptedAccessToken()[7:]
            })
        r = self.server.postContent(url, data=data, headers=headers, files=files)
        if r.status_code != 201:
            raise Exception('Upload %s failure.' % type)
        return objId
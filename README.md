# python-downloader
A set of python and config files to allow you to download files from a URL

##Overview:
These scripts allow you to configure a website URL where it will download all images over a configured size (100KB default). Currently the script processes each URL sequentially so can be slow to process, but it functionally works.
 
##Dependencies required (python libraries):
- python3
- urllib
- BeautifulSoup4
- logging

##Usage notes: 
python testDownloader.py

##Configuration options explained:
- [URL]
  - base: http://imgur.com/r/funny **The base URL to download**
  - retries: 2 **The HTTP retries setting - not currently being used**
  - maxDepth: 0 **How far to follow any links on the page - this setting is troublesome and should be left at the default**
  - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36

- [OUTPUT] **Options for anything downloaded**
  - ; This should end with /
  - outputFolder: ./images/
  - includeDateInOutputName: true **Include the date in the output folder name**
  - outputTmpFolderPrefix: tmp_ **The location to download any temporary files. This value is prefixed to the name above**
  - ; Measured in k
  - minimumFileSize: 100 **The minimum file size to download, measured in Kb**
  - minimumContentLength: 10000 **The minimum content length for the file, as returned by the server**
  - downloadVideos: true **Whether or not to try to download videos**

- [LOGGER] **The error log configuration**
  - filename: downloader.log
  - level: DEBUG
  - includeDateInName: true

- [ACCESSLOGGER] **The access log configuration**
  - filename: access.log
  - level: INFO
  - includeDateInName: true

[EXTENSIONS] **File extensions listed here are attempted to be downloaded**  
  type1: .png  
  type2: .jpg  
  type3: .jpeg  
  type4: .gif  
  type5: .bmp  
  type6: .webm  
  type7: .mp4  
  
[EXCEPTIONS]  
  ; blacklisted urls  
  url01: myfreecams.com **URLs (or partial URLs) listed here are ignored for processing**  


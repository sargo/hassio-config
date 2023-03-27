#!/bin/bash
{

pidfile=/tmp/record_staircase_pidfile
if [ -f "$pidfile" ] && kill -0 `cat $pidfile` 2>/dev/null; then
    echo still running
    exit 1
fi
echo $$ > $pidfile

folder=/media/data/recordings
id=staircase_$(date +"%Y%m%d%H%M%S")
http_url=http://10.10.0.105:8888
ffmpeg -hide_banner -use_wallclock_as_timestamps 1 -i $http_url -r 5 -vsync 0 -c copy -frames:v 150 -metadata:s:v:0 rotate=270 $folder/$id.mp4

#find $folder -type f -name *.mp4 -mtime +30 -exec rm {} ;

} 2>&1 | tee -a /home/homeassistant/logs/record_staircase.log


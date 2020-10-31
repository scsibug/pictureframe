# Display the oldest file, then delete it.
album_path = /home/pi/album
f=$(ls -tc $album_path | head -n 1)
if [[ -f $f ]]; then
    epd_write 0 0 $album_path/$f
    rm $album_path/$f

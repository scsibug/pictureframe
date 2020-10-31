# Display the oldest file, then delete it.
# epd_write should be the IT8951 binary
album_path=/home/pi/album
f=$(ls -tc $album_path | head -n 1)
if [[ -f $album_path/$f ]]; then
    epd_write 0 0 $album_path/$f
    rm $album_path/$f
fi

for file in raw/*
do
	base_file=`basename $file`
	ffmpeg -y -hide_banner -loglevel error -i "$file" -ac 1 "wav/${base_file%.*}.wav" 1>/dev/null
done

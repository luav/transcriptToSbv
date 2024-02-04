# transcriptToSbv
It converts a segment of the YouTube transcript into SBV format and adjusts the start time.

This script is useful when you would like to copy a segment of the YouTube transcript either in the SBV format form the YouTube Studio or in the raw format from any public YouTube video, adjust that transcript, and upload it into your YouTube Studio in the SBV format.

## Usage
```
$ ./transcriptToSbv.py -h
usage: transcriptToSbv.py [-h] [-s START_TIME] [-n] inpfs [inpfs ...]

Transcript adjuster and converter to the [SBV](https://docs.fileformat.com/settings/sbv/) format
from either SBV or raw format yielded by YouTube

positional arguments:
  inpfs                 Input file names of the transcripts to be adjusted or converted

options:
  -h, --help            show this help message and exit
  -s START_TIME, --start-time START_TIME
                        Adjust start time of subtitles to the specified [[h:]m:]s.ms (default:
                        None)
  -n, --no-overwrites   Never overwrite the output file, omitting the processing if that case
                        (default: False)
```

## Use-case
You would like to copy a segment of the YouTube video with its automatic transcript, refine that transcript (e.g., fix syntax for the proper translation), and upload them to your YouTube Studio.

However, the outlined use-case implies 2 task, which are automated by this script:
1. YouTube Studio requires transcript (subtitles) in the SBV format, which differs from the publicly available transcripts in YouTube.
2. The copied segment of the video requires shifting the start time of the respecting segment of transcript.

The format of publicly available transcripts is:
```
0:03
Subtitle0
m1:ss1
Subtitle1_long
h2:mm2:ss2
Subtitle2
h3:mm3:ss3
Subtitle3
...
```
You might want introduce some notes when refining that transcript, and slit long subtitles (e.g., dialogs) into several lines, which results in the following format:
```
# Optional header comments

m1:ss1
Subtitle1
- Subtitle1 continuation
- Subtitle1 continuation2

h2:mm2:ss2
Subtitle2
h3:mm3:ss3
Subtitle3
...
```
Then, you can use this script to convert the transcript into the SBV format and adjust the start time of subtitles as follows:
```sh
$ ./transcriptToSbv.py -s 0 modified_raw_transcript.txt
```
It will produce `modified_raw_transcript.sbv` (or `modified_raw_transcript.fix.sbv` if the input file has `.sbv` extension):
```
0:00:00.000,0:muf1:suf1.msuf1
Subtitle1
- Subtitle1 continuation
- Subtitle1 continuation2

hus2:mus2:sus2.msus2,huf2:muf2:suf2.msuf2
Subtitle2

hus3:mus3:sus3.msus3,huf3:muf3:suf3.msuf3
Subtitle3
...
```

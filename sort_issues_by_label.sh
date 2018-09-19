#!/bin/bash

INFILE="issues.txt"
OUTFILE="issues_by_label.txt"
# GREP="ag --nonumbers" # http://geoff.greer.fm/ag
GREP=$( which grep )

rm -f "$OUTFILE"

write_to_file() {
    echo "$1" >> "$OUTFILE"
}

write_to_file "### Early Phase\n"
$GREP early "$INFILE" | sed -e 's/(.early.)//g'  >> "$OUTFILE"
write_to_file

write_to_file "### CfP Phase\n"
$GREP cfp "$INFILE" | sed -e 's/(.cfp phase.)//g' >> "$OUTFILE"
write_to_file

write_to_file "### Pre-conf Phase\n"
$GREP preconf "$INFILE" | sed -e 's/(.preconf.)//g' >> "$OUTFILE"
$GREP pre-conf "$INFILE" | sed -e 's/(.pre-conf.)//g' >> "$OUTFILE"
write_to_file

write_to_file "### Last month Phase\n"
$GREP "last month" "$INFILE" | sed -e 's/(.last\smonth.)//g' >> "$OUTFILE"
write_to_file

write_to_file "### Last week Phase\n"
$GREP "last week" "$INFILE" | sed -e 's/(.last\sweek.)//g' >> "$OUTFILE"
write_to_file

write_to_file "### Post conference\n"
$GREP after "$INFILE" >> "$OUTFILE"
$GREP postconf "$INFILE" >> "$OUTFILE"
$GREP "post conf" "$INFILE" >> "$OUTFILE"

echo "$OUTFILE has been created"

exit 0

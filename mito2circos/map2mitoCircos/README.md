![example](http://ogj9k5cjf.bkt.clouddn.com/circos.png)
example: mapping reads to some candidate preys' mitogenome.

#### Summary
circos is very powerful software to illustrate genetic information, especially for mitochondrion and chloroplast genomes. Here I provide a useful python script to convert mapping depth information to a image.

#### Requirement

Overall, circos must be installed in your computer, though it is a little difficult to install.

then there file are needed: (see these files in current directory)

- references.fa
- depth.txt
- map2mitoCircos.conf

```perl
# where circos you install
circos_path		=	/usr/local/bin/circos
# whether draw depth abundance circle
depth_fill		= 	vdgreen
# locus name's clolor showed on center of circle
locus_color		=	black
# gene name label color
label_color		=	black
# image
outdir			=	./outdir
png				=	yes
svg				=	yes
# color or file
background		=	white
```
let's get ball running.
```bash
python3 map_mito_depth.py  -fa references.fa -map depth.txt -conf map2mitoCircos.conf
```

#### See more
recommend some good learning resources:

- http://qiubio.com/circos教程
- http://circos.ca/

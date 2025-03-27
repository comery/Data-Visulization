library(ggplot2)
args<-commandArgs()
if (! args[1]) {
	stop("No input fasta !")
}

paf = read.table(args[1], sep="\t")
ggplot(data=paf, aes(x=V3, xend=V4, y=V8, yend=V9, color=factor(V1))) + geom_segment() + labs(x="Reference coordinate", y="Query coordinate")

all: ngram.native karel.native

BUILD = corebuild
FLAGS = -use-ocamlfind -use-menhir

%.native: always
	$(BUILD) $(FLAGS) src/$@

clean:
	rm -rf *.native *.top _build

always:

.PHONY: always

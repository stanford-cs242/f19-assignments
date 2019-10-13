all: ngram.native karel.native
debug: ngram.byte karel.byte

BUILD = corebuild
FLAGS = -use-ocamlfind -use-menhir

%.byte: always
	$(BUILD) $(FLAGS) src/$@

%.native: always
	$(BUILD) $(FLAGS) src/$@

clean:
	rm -rf *.byte *.native *.top _build

always:

.PHONY: always

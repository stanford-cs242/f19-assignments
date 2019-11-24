all: main.native
debug: main.byte

BUILD = corebuild
FLAGS = -use-ocamlfind -use-menhir

%.byte: always
	$(BUILD) $(FLAGS) src/$@

%.native: always
	$(BUILD) $(FLAGS) src/$@

clean:
	rm -rf main.byte main.native *.top _build

always:

.PHONY: always

all: exercise1.native exercise2.native

BUILD = corebuild
FLAGS = -use-ocamlfind

%.native: always
	$(BUILD) $(FLAGS) $@

clean:
	rm -rf *.native *.top _build

always:

.PHONY: always

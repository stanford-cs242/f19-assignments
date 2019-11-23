include $(FSTAR_HOME)/ulib/ml/Makefile.include
include $(FSTAR_HOME)/examples/Makefile.include

all: nfs_server nfs_server_test

nfs_server: out NFS.Server.fst
	$(FSTAR) $(FSTAR_DEFAULT_ARGS) --odir out --codegen OCaml --extract 'NFS.Server' \
		NFS.Server.fst --record_hints
	$(OCAMLOPT) -c out/NFS_Server.ml -I out

nfs_server_test: out NFS.Server.Test.fst
	$(FSTAR) $(FSTAR_DEFAULT_ARGS) --odir out --codegen OCaml --extract 'NFS.Server.Test' \
		NFS.Server.Test.fst --record_hints
	$(OCAMLOPT) -c out/NFS_Server_Test.ml -I out
	$(OCAMLOPT) -o nfs_tests.exe out/NFS_Server.cmx out/NFS_Server_Test.cmx

out:
	mkdir -p out

clean:
	rm -rf out *~ *.exe *.hints

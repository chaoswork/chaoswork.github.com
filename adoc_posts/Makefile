SOURCE = $(wildcard *.adoc)  
OBJS = $(patsubst %.adoc,%.html,$(SOURCE))  


%.html:%.adoc
	asciidoctor $< -o $@
	sed -i "" 's/<!DOCTYPE html>//g' $@
	python html_in_md.py $@

all: $(OBJS)
	@echo "Success"

clean:
	rm -rf *.html

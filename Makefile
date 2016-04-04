SUBDIRS=adoc_posts
define make_subdir
 @for subdir in $(SUBDIRS) ; do \
	  ( cd $$subdir && make $1 ) \
	   done;
 endef
all:
	 $(call make_subdir , all)
	 jekyll build
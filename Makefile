CC=gcc
CFLAGS=-c -Wall
LDFLAGS=
SOURCES=lsdata_api.c lsdata_test.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=hello
all: $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)
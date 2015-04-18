CC=gcc
CFLAGS=-c -Wall
LDFLAGS=
SOURCES=gdd_api.c gdd_test.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=gdd_test
all: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)
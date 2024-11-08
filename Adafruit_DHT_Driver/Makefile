CC = gcc
CFLAGS =  -std=c99 -I. -lbcm2835
DEPS = 
OBJ = Adafruit_DHT.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

Adafruit_DHT: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)
	strip $@

clean:
	rm -f $(OBJ)

realclean: clean
	rm -f Adafruit_DHT

test:
	sudo ./Adafruit_DHT 22 4

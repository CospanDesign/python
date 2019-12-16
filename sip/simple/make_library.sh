NAME=word
echo "Create the position independent code"
gcc -c -Wall -Werror -fpic ${NAME}.cpp

echo "Create the chared object library from the object file"
gcc -shared -o lib${NAME}.so ${NAME}.o

echo "Copy the shared object library over to the use library"
sudo cp lib${NAME}.so /usr/lib

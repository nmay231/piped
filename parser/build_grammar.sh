if [ -w ./Piped.g4 ]; then
    /usr/lib/jvm/java-11-openjdk-amd64/bin/java -jar /usr/local/lib/antlr-4.8-complete.jar -Dlanguage=Python3 -o grammar Piped.g4;
fi;
if [ -w ../Piped.g4 ]; then
    /usr/lib/jvm/java-11-openjdk-amd64/bin/java -jar /usr/local/lib/antlr-4.8-complete.jar -Dlanguage=Python3  ../Piped.g4;
fi;
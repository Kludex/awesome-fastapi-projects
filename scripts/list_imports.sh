
for file in $(find reps -maxdepth 1 -type d); do
    	grep -r "import" --include \*.py $file > imports.txt
done

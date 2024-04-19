# Rename PDF files by stripping final number

list_objects=$(aws s3 ls s3://camille-data/PDF/B14138/$1/ | awk '{print $4}')

for old_object_name in $list_objects; do
    #echo $old_object_name
    new_object_name=$(echo $old_object_name | awk '{sub("_29[0-9]{6}", "")}1')
    #echo $new_object_name
    aws s3 mv s3://camille-data/PDF/B14138/$1/$old_object_name s3://camille-data/PDF/B14138/$1/$new_object_name
done
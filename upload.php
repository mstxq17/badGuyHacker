<?php
if(!file_exists("./upload")){
    mkdir('./upload');
}
if($_FILES['file']){
    $ext = end(explode('.', $_Files['file']['name']));
    $filename = './upload/' + md5(time()) + '.' + $ext;
    move_uploaded_file($_FILES['file']['tmp_name'],$filename);
    echo "stored in :".$filename;
}else{
    echo "please upload file,parameter is file!";
}
?>
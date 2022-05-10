<?php

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, 'http://127.0.0.1:5000/classify'); //replace w url
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_POST, 1);

$cfile = curl_file_create('C:\inetpub\wwwroot\classify-api\test\data\civ\civ_1.pdf','file/pdf','civ_1.pdf');

$post = array(
    'client' => 'a2b',
    'file' => curl_file_create('C:\inetpub\wwwroot\classify-api\test\data\civ\civ_1.pdf','file/pdf','civ_1.pdf')
);

curl_setopt($ch, CURLOPT_POSTFIELDS, $post);

$result = curl_exec($ch);
echo $result;
if (curl_errno($ch)) {
    echo 'Error:' . curl_error($ch);
}
curl_close($ch);



?>


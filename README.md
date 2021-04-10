## 使用方法（How to use）
```
<?php
$result = system('python3 /var/www/html/ocr/read_card_number.py "test.png"');

var_dump(json_decode($result));
object(stdClass)#1 (2) {
  ["result"]=>
  string(2) "OK"
  ["data"]=>
  string(16) "3337400323693929"
}
OR
object(stdClass)#1 (2) {
  ["result"]=>
  string(2) "NG"
  ["data"]=>
  string(0) ""
}
```

<?php

namespace mxlims\tools\php\test\ExampleAndTestJson;

require_once __DIR__ . '/../../src/Utils/Utils.php';

use Exception;
use PHPUnit\Framework\TestCase;
use mxlims\tools\php\src\Utils\Utils;

class TestJsonTest extends TestCase {

	public static function getTestJsonFiles(): array {
		$path=realpath(__DIR__).'/../../../../test/json';
		$rii = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($path));
		$files = array();
		foreach ($rii as $file){
			if (!$file->isDir()) {
				$files[] = [realpath($file->getPathname())];
			}
		}
		return $files;
	}

	/**
	 * @dataProvider getTestJsonFiles
	 * @throws Exception
	 */
	public function testValidityOfTestJsonFilesIsCorrect($fullJsonPath) {
		if(!str_ends_with($fullJsonPath,'.json')){
			throw new Exception('Path should end with .json');
		}
		$fullJsonPath=str_replace('\\', '/', $fullJsonPath);
		$jsonPath=substr(strstr($fullJsonPath, '/test/json/'), 11);
		$parts=explode('/', $jsonPath);
		if(3!==count($parts)){
			throw new Exception('Splitting on / should give 3 parts, got '.count($parts));
		}
		$expectValid=false;
		if('valid'===$parts[1]){
			$expectValid=true;
		} else if('invalid'!==$parts[1]){
			throw new Exception('Expected "valid" or "invalid", got '.$parts[1]);
		}
		$schemaPath=$parts[0].'/';
		$parts=explode('_', $parts[2]);
		$schemaPath.=$parts[0].'.json';
		$message="$jsonPath should be ".($expectValid?'valid':'invalid')." against $schemaPath but was ".($expectValid?'invalid':'valid');
		$this->assertEquals($expectValid, Utils::validateTestJsonFileAgainstSchema($jsonPath, $schemaPath), $message);
	}

}
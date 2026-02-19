<?php

namespace mxlims\tools\php\test\ExampleAndTestJson;

require_once __DIR__ . '/../../src/Utils/Utils.php';

use Exception;
use PHPUnit\Framework\TestCase;
use mxlims\tools\php\src\Utils\Utils;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;

class TestJsonTest extends TestCase {

	public static string $schemaFileContainingVersion='messages/BaseMessageData.json';
	public static string $pathToVersionInSchemaFile='/properties/version/const';

	/**
	 * Determines the current local schema version, finds the corresponding test JSON directory, and returns all files under that directory.
	 * @throws Exception
	 */
	public static function getTestJsonFiles(): array {

		//Check that the specified schema file exists and is valid JSON
		$file=@file_get_contents(realpath(__DIR__).'/../../../../schemas/'.static::$schemaFileContainingVersion);
		if(!$file){ throw new Exception('Could not open schema file to determine version: '.static::$schemaFileContainingVersion); }
		$obj=json_decode($file, true);
		if(!$obj){ throw new Exception(static::$schemaFileContainingVersion.' is not valid JSON; cannot determine local schema version'); }

		//Attempt to traverse the JSON to find the version, which should look like "0.9", "1.2.3", etc.
		$path=explode('/', trim(static::$pathToVersionInSchemaFile, '/'));
		foreach ($path as $node) {
			if(!isset($obj[$node])){ throw new Exception('Cannot determine local schema version; cannot follow path '.static::$pathToVersionInSchemaFile.' in '.static::$schemaFileContainingVersion); }
			$obj=$obj[$node];
		}
		$version=$obj;
		if(!preg_match('/^\d+(\.\d+)+$/', $version)){
			throw new Exception($version.' does not look like a valid version number in '.static::$schemaFileContainingVersion.static::$pathToVersionInSchemaFile);
		}

		//Verify that a v[version] directory exists under test/json, and return a list of all files under it
		$path=realpath(__DIR__).'/../../../../test/json/v'.$version;
		if(!file_exists($path)){
			throw new Exception("Test JSON path $path does not exist");
		}
		$rii = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path));
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
		//basic sanity checking
		if(!str_ends_with($fullJsonPath,'.json')){
			throw new Exception('Path should end with .json');
		}
		$fullJsonPath=str_replace('\\', '/', $fullJsonPath);
		$jsonPath=substr(strstr($fullJsonPath, '/test/json/'), 11);

		//Split on /valid/ or /invalid/ to determine whether test file should be valid against schema
		$expectValid=true;
		$parts=explode('/valid/', $jsonPath);
		if(1===count($parts)){
			$expectValid=false;
			$parts=explode('/invalid/', $jsonPath);
		}
		if(1===count($parts)){
			throw new Exception('Path did not contain /valid/ or /invalid/');
		}

		//discard version number, append .json to get schema path relative to /schemas/
		$parts=explode('/', $parts[0], 2);
		$schemaPath=$parts[1].'.json';

		$message="test/json/$jsonPath should be ".($expectValid?'valid':'invalid')." against schemas/$schemaPath but was ".($expectValid?'invalid':'valid');
		$this->assertEquals($expectValid, Utils::validateTestJsonFileAgainstSchema($jsonPath, $schemaPath), $message);
	}

}
<?php

namespace mxlims\tools\php\src\Utils;

require __DIR__ . '/../../vendor/opis/json-schema-2.6.0/autoload.php';
require __DIR__ . '/../../vendor/opis/uri-1.1.0/autoload.php';

use Exception;
use Opis\JsonSchema\Errors\ValidationError;
use Opis\JsonSchema\SchemaLoader;
use Opis\JsonSchema\Validator;
use Opis\Uri\Uri;

class Utils {

	/**
	 * Validate JSON string against a root JSON Schema (Draft-07) with all relative $refs.
	 * DO NOT ATTEMPT TO "OPTIMISE" THIS GHASTLY MESS. Opis' API is "special". It even made ChatGPT cry.
	 * Every line here is necessary, and you WILL break it if you try to make it rational and sane. HERE BE DRAGONS.
	 *
	 * @param string $jsonString JSON string to validate
	 * @param string $rootSchemaPath Path to root schema on disk
	 * @return bool True if valid, false otherwise
	 * @throws \RuntimeException on invalid JSON or missing schema
	 */
	public static function opis_validateJsonAgainstSchema(string $jsonString, string $rootSchemaPath): bool {
		// Normalize root schema path
		$rootSchemaPath = realpath($rootSchemaPath);
		if (!$rootSchemaPath) {
			throw new \RuntimeException("Root schema file not found: $rootSchemaPath");
		}
		$rootSchemaPath = str_replace('\\', '/', $rootSchemaPath);

		// Load JSON input
		$jsonData = json_decode($jsonString);
		if (!$jsonData) {
			throw new \RuntimeException('Invalid JSON input');
		}

		// Loader and validator
		$loader = new SchemaLoader();
		$validator = new Validator($loader);

		// Internal helper: load a schema file and all relative $refs
		$loadSchemaFile = function (string $path) use ($loader, &$loadSchemaFile) {
			$path = realpath($path);
			if (!$path) {
				throw new \RuntimeException("Schema file not found: $path");
			}
			$path = str_replace('\\', '/', $path);

			$schema = json_decode(file_get_contents($path));
			if (!$schema) {
				throw new \RuntimeException("Invalid JSON schema at $path");
			}

			// Base URI for this schema
			$uri = new Uri([
				'scheme' => 'file',
				'host' => null,
				'path' => $path
			]);

			// Load schema into loader
			$loader->loadObjectSchema($schema, $uri);

			// Preload all relative $refs recursively
			$dir = dirname($path);
			$queue = [$schema];
			while ($q = array_shift($queue)) {
				if (is_object($q) || is_array($q)) {
					foreach ($q as $k => $v) {
						if ($k === '$ref' && is_string($v) && !preg_match('#^[a-z]+://#i', $v)) {
							$refPath = $dir . '/' . $v;
							if (file_exists($refPath)) {
								$loadSchemaFile($refPath);
							}
						} elseif (is_object($v) || is_array($v)) {
							$queue[] = $v;
						}
					}
				}
			}
		};

		// Load root schema + all relative refs
		$loadSchemaFile($rootSchemaPath);

		// Get the root schema object for validation
		$rootSchemaJson = json_decode(file_get_contents($rootSchemaPath));
		$rootUri = new Uri([
			'scheme' => 'file',
			'host' => null,
			'path' => $rootSchemaPath
		]);
		$rootSchema = $loader->loadObjectSchema($rootSchemaJson, $rootUri);

		// Validate
		$result = $validator->validate($jsonData, $rootSchema);

		if ($result->isValid()) {
			return true;
		}

		$printLeafErrors = function (ValidationError $error) use (&$printLeafErrors) {

			if (count($error->subErrors()) === 0) {

				// Build message with placeholders replaced
				$message = $error->message();
				foreach ($error->args() as $key => $value) {
					if (is_array($value)) {
						$value = implode(', ', $value);
					} elseif (is_object($value)) {
						$value = json_encode($value);
					}
					$message = str_replace('{' . $key . '}', (string)$value, $message);
				}

				// Build JSON Pointer from path segments (Opis 2.6.0)
				$path = $error->data()->path();
				if (empty($path)) {
					$pointer = '<root>';
				} else {
					$escaped = array_map(
						fn($p) => str_replace(['~', '/'], ['~0', '~1'], (string)$p),
						$path
					);
					$pointer = '/' . implode('/', $escaped);
				}

				echo /*$pointer ': '.*/ $message . PHP_EOL;
				return;
			}

			foreach ($error->subErrors() as $sub) {
				$printLeafErrors($sub);
			}
		};

		$printLeafErrors($result->error());
		return false;
	}

	public static function validateJsonAgainstSchema(string $jsonString, string $schemaPath): bool {
		$rootSchemaPath = rtrim(str_replace('\\', '/', realpath(__DIR__ . '/../../../../schemas/')), '/') . '/' . $schemaPath;
		return Utils::opis_validateJsonAgainstSchema($jsonString, $rootSchemaPath);
	}

	/**
	 * @param string $testJsonPath The path of the test JSON from  mxlims/test/json/, e.g., "valid/validJson.json"
	 * @param string $schemaPath The path of the schema file to validate against, from mxlims/schemas, e.g., "datatypes/ImageRegion.json"
	 * @return bool
	 * @throws \Exception
	 */
	public static function validateTestJsonFileAgainstSchema(string $testJsonPath, string $schemaPath): bool {
		$testJsonPath = rtrim(str_replace('\\', '/', realpath(__DIR__ . '/../../../../test/json/')), '/') . '/' . ltrim($testJsonPath, '/');
		if (!@file_exists($testJsonPath)) {
			throw new \Exception("$testJsonPath does not exist");
		}
		$jsonString = @file_get_contents($testJsonPath);
		if (!$jsonString) {
			throw new \Exception("Could not open test JSON for reading: $testJsonPath");
		}
		return Utils::validateJsonAgainstSchema($jsonString, $schemaPath);
	}

	/**
	 * @param $json
	 * @return bool
	 * @throws Exception
	 */
	public static function validateIndividualJsonElementsAgainstSchema($json): bool {
		$schemaDir = str_replace('/', DIRECTORY_SEPARATOR, __DIR__ . '/../../../../schemas/');
		$array = json_decode($json, true);
		$isValid = true;
		foreach (array_keys($array) as $objectType) {
			if ('version' === $objectType) {
				continue;
			}
			if (!isset($array[$objectType])) {
				throw new Exception("JSON does not contain $objectType, or it is empty");
			}
			if (file_exists($schemaDir . 'data' . DIRECTORY_SEPARATOR . $objectType . '.json')) {
				$schemaFile = 'data' . DIRECTORY_SEPARATOR . $objectType . '.json';
			} else if (file_exists($schemaDir . 'objects' . DIRECTORY_SEPARATOR . $objectType . '.json')) {
				$schemaFile = 'objects' . DIRECTORY_SEPARATOR . $objectType . '.json';
			} else {
				throw new Exception("Cannot find $objectType.json in schemas/data or schemas/objects");
			}
			$objects = $array[$objectType];
			$keys = array_keys($objects);
			foreach ($keys as $key) {
				$obj = $objects[$key];
				$json = json_encode($obj, JSON_PRETTY_PRINT);
				if (!Utils::validateJsonAgainstSchema($json, $schemaFile)) {
					echo "$objectType/$key did not validate against schema\n";
					$isValid = false;
				}
			}
		}
		return $isValid;
	}
}
<?php

namespace mxlims\tools\php\test\ExampleAndTestJson;

require_once __DIR__ . '/../../src/Utils/Utils.php';

use Exception;
use PHPUnit\Framework\TestCase;
use mxlims\tools\php\src\Utils\Utils;

class ExampleJsonTest extends TestCase {

	/**
	 * Data provider for testExampleFilesAreValid
	 * Each element contains:
	 * - exampleFile: The path from mxlims_data_model/docs/examples/
	 * - schema: The path from mxlims_data_model/mxlims/schemas/
	 * @return array[]
	 */
	public static function getExampleFiles(): array {
		return [
			[['exampleFile'=>'Shipment_singlePositionPins.json','schema'=>'messages/ShipmentMessage.json']],
			[['exampleFile'=>'Shipment_multiPositionPins.json','schema'=>'messages/ShipmentMessage.json']],
			[['exampleFile'=>'Shipment_plates.json','schema'=>'messages/ShipmentMessage.json']]
		];
	}

	/**
	 * @dataProvider getExampleFiles
	 * @throws Exception
	 */
	public function testExampleFilesAreValid($example) {
		$exampleFile=$example['exampleFile'];
		$schema=$example['schema'];
		$examplesDir=realpath(__DIR__.'/../../../../../docs/examples/');
		$this->assertDirectoryExists($examplesDir);
		$path=rtrim($examplesDir,'/').'/'.$exampleFile;
		self::assertFileExists($path);
		$json=@file_get_contents($path);
		self::assertNotFalse($json, "Could not open $path");
		$this->assertTrue(Utils::validateIndividualJsonElementsAgainstSchema($json), "$exampleFile: At least one element failed schema validation");
		$this->assertTrue(Utils::validateJsonAgainstSchema($json, $schema), "$exampleFile: All elements validated but the whole message failed validation against $schema");
	}


}
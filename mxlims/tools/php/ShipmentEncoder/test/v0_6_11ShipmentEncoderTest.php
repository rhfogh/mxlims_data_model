<?php

namespace mxlims\tools\php\ShipmentEncoder\test;

include_once 'v0_6_10ShipmentEncoderTest.php';

class v0_6_11ShipmentEncoderTest extends v0_6_10ShipmentEncoderTest {

	public static string $fileWithSchemaVersion = __DIR__ . '/../../../../schemas/messages/BaseMessageData.json';
	public static array $pathToVersion = ['properties', 'version', 'const'];

}

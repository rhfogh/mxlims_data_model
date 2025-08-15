<?php

namespace mxlims\tools\php\ShipmentEncoder\test;

include_once 'v0_6_5ShipmentEncoderTest.php';

class v0_6_7ShipmentEncoderTest extends v0_6_5ShipmentEncoderTest {
	// Overwrite any 0.6.4 tests here, and add new ones.
	public function testGenerateUuid() {
		$uuid=$this->encoder->generateUuid();
		self::assertMatchesRegularExpression('/^[a-f0-9]{8}-[a-f0-9]{4}-[\d][a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}$/', $uuid);
	}

}

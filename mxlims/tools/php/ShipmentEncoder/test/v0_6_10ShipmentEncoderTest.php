<?php

namespace mxlims\tools\php\ShipmentEncoder\test;

include_once 'v0_6_7ShipmentEncoderTest.php';

class v0_6_10ShipmentEncoderTest extends v0_6_7ShipmentEncoderTest {

	public static string $fileWithSchemaVersion=__DIR__.'/../../../../schemas/messages/BaseMessageData.json';
	public static array $pathToVersion=['properties','version','const'];


	public function testCreateShipment() {
		$shipment = $this->encoder->createShipment('mx4025', 1);
		$this->assertEquals('mx4025', $shipment['proposalCode']);
		$this->assertEquals(1, $shipment['sessionNumber']);
		$this->assertEquals('Shipment', $shipment['mxlimsType']);
		$this->assertNotEmpty($shipment['uuid']);
		$this->assertEquals(1, $shipment['index']);
	}

	public function testCreateShipmentNoSessionNumber() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->assertEquals('mx4025', $shipment['proposalCode']);
		$this->assertArrayNotHasKey('sessionNumber', $shipment);
		$this->assertEquals('Shipment', $shipment['mxlimsType']);
		$this->assertNotEmpty($shipment['uuid']);
	}

	public function testCreateShipmentNullSessionNumber() {
		$shipment = $this->encoder->createShipment('mx4025', null);
		$this->assertEquals('mx4025', $shipment['proposalCode']);
		$this->assertArrayNotHasKey('sessionNumber', $shipment);
		$this->assertEquals('Shipment', $shipment['mxlimsType']);
		$this->assertNotEmpty($shipment['uuid']);
	}

	public function testAddPlatePointDropRegionByPlateDropIndex(){
		$drop=$this->createPlateAndDrop();
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->assertArrayHasKey('region', $region);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertEquals('#/WellDrop/WellDrop'.$drop['index'], $region['containerRef']['$ref']);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
		$this->assertEquals('micron', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
	}

	public function testAddImagePointDropRegionByPlateDropIndex(){
		$drop=$this->createPlateAndDrop();
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'image/jpeg', 'http://image.url/1234');
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
		$this->assertEquals('#/WellDrop/WellDrop'.$drop['index'], $region['containerRef']['$ref']);
		$this->assertArrayHasKey('region', $region);
		$this->assertEquals('pixel', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
	}

}

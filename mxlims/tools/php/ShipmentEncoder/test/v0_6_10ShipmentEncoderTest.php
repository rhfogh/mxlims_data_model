<?php

namespace mxlims\tools\php\ShipmentEncoder\test;

include_once 'v0_6_7ShipmentEncoderTest.php';

class v0_6_10ShipmentEncoderTest extends v0_6_7ShipmentEncoderTest {

	public static string $fileWithSchemaVersion = __DIR__ . '/../../../../schemas/messages/BaseMessageData.json';
	public static array $pathToVersion = ['properties', 'version', 'const'];


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

	public function testAddPlatePointDropRegionByPlateDropIndex() {
		$drop = $this->createPlateAndDrop();
		$region = $this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->assertArrayHasKey('region', $region);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertEquals('#/WellDrop/WellDrop' . $drop['index'], $region['containerRef']['$ref']);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
		$this->assertEquals('micron', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
	}

	public function testAddImagePointDropRegionByPlateDropIndex() {
		$drop = $this->createPlateAndDrop();
		$region = $this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'image/jpeg', 'http://image.url/1234');
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
		$this->assertEquals('#/WellDrop/WellDrop' . $drop['index'], $region['containerRef']['$ref']);
		$this->assertArrayHasKey('region', $region);
		$this->assertEquals('pixel', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
	}

	public function testAddIdentifierToObject() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->encoder->addIdentifierToObject($shipment, 'test.icebear.fi', 69420);
		$shipment = $this->encoder->get('Shipment', $shipment['index']);
		$this->assertArrayHasKey('identifiers', $shipment);
		$this->assertArrayHasKey('test.icebear.fi', $shipment['identifiers']);
		$this->assertEquals(69420, $shipment['identifiers']['test.icebear.fi']);
	}

	public function testAddIdentifierToObjectBadDomainName() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->expectExceptionMessageMatches('/^Bad domain name/');
		$this->encoder->addIdentifierToObject($shipment, 'bogus', 69420);
	}

	public function testAddUrlToObject() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->encoder->addUrlToObject($shipment, 'test.icebear.fi', 'https://test.icebear.fi/shipment/1');
		$shipment = $this->encoder->get('Shipment', $shipment['index']);
		$this->assertArrayHasKey('urls', $shipment);
		$this->assertArrayHasKey('test.icebear.fi', $shipment['urls']);
		$this->assertEquals('https://test.icebear.fi/shipment/1', $shipment['urls']['test.icebear.fi']);
	}

	public function testAddUrlToObjectBadDomainName() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->expectExceptionMessageMatches('/^Bad domain name/');
		$this->encoder->addUrlToObject($shipment, 'bogus', 'https://test.icebear.fi/shipment/1');
	}

	public function testAddIdentifierAndUrlToObject() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->encoder->addIdentifierAndUrlToObject($shipment, 'test.icebear.fi', 69420, 'https://test.icebear.fi/shipment/1');
		$shipment = $this->encoder->get('Shipment', $shipment['index']);
		$this->assertArrayHasKey('identifiers', $shipment);
		$this->assertArrayHasKey('test.icebear.fi', $shipment['identifiers']);
		$this->assertEquals(69420, $shipment['identifiers']['test.icebear.fi']);
		$this->assertArrayHasKey('urls', $shipment);
		$this->assertArrayHasKey('test.icebear.fi', $shipment['urls']);
		$this->assertEquals('https://test.icebear.fi/shipment/1', $shipment['urls']['test.icebear.fi']);
		var_dump($shipment);
	}


	public function testDropImageInvalidWithoutUrlAndData() {
		$schemaPath = 'datatypes/DropImage.json';
		$obj = json_decode('{ "mimeType":"image/jpeg" }', true);
		$this->assertFalse($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage should not be valid with neither url nor data');
	}

	public function testDropImageValidWithUrlWithoutData() {
		$schemaPath = 'datatypes/DropImage.json';
		$obj = json_decode('{ "mimeType":"image/jpeg" }', true);
		$obj['url'] = "https://icebear.fi";
		$this->assertTrue($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage should be valid with url but not data');
	}

	public function testDropImageValidWithoutUrlWithData() {
		$schemaPath = 'datatypes/DropImage.json';
		$obj = json_decode('{ "mimeType":"image/jpeg" }', true);
		$obj['data'] = "Some image data here";
		$this->assertTrue($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage should be valid with data but not url');
	}

	public function testDropImageInvalidWithUrlAndData() {
		$schemaPath = 'datatypes/DropImage.json';
		$obj = json_decode('{ "mimeType":"image/jpeg" }', true);
		$this->assertFalse($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage should not be valid with neither url nor data');
		$obj['url'] = "https://icebear.fi";
		$obj['data'] = "Some image data here";
		$this->assertFalse($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage should not be valid with both url and data');
	}

	private string $imageRegionJson = '{
			"image":{
			  "mimeType":"image/jpeg"
			},
			"region":{
			  "regionType":"point",
			  "x":785,
			  "y":400
			},
			"units":"pixel"
	    }';

	public function testImageRegionDropImageInvalidWithoutUrlAndData() {
		$schemaPath = 'datatypes/ImageRegion.json';
		$obj = json_decode($this->imageRegionJson, true);
		$this->assertFalse($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage in ImageRegion should not be valid with neither url nor data');
	}

	public function testImageRegionDropImageValidWithUrlWithoutData() {
		$schemaPath = 'datatypes/ImageRegion.json';
		$obj = json_decode($this->imageRegionJson, true);
		$obj['image']['url'] = "https://icebear.fi";
		$this->assertTrue($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage in ImageRegion should be valid with url and no data');
	}

	public function testImageRegionDropImageValidWithoutUrlWithData() {
		$schemaPath = 'datatypes/ImageRegion.json';
		$obj = json_decode($this->imageRegionJson, true);
		$obj['image']['data'] = "Some image data here";
		$this->assertTrue($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage in ImageRegion should be valid with data and no url');
	}

	public function testImageRegionDropImageInvalidWithUrlAndData() {
		$schemaPath = 'datatypes/ImageRegion.json';
		$obj = json_decode($this->imageRegionJson, true);
		$obj['image']['url'] = "https://icebear.fi";
		$obj['image']['data'] = "Some image data here";
		$this->assertFalse($this->validateJsonAgainstSchema(json_encode($obj), $schemaPath), 'DropImage in ImageRegion should not be valid with both url and data');
	}

}

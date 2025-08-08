<?php

namespace mxlims\tools\php\ShipmentEncoder\src;

include_once __DIR__.'/ShipmentEncoderInterface.php';
include_once __DIR__.'/v0_6_5ShipmentEncoder.php';

class v0_6_7ShipmentEncoder extends v0_6_5ShipmentEncoder {

	public function generateUuid(): string {
		$uuid=parent::generateUuid();
		$uuid[14]=rand(1,5);
		return $uuid;
	}

}


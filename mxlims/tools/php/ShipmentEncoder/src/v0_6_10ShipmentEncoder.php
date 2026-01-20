<?php

namespace mxlims\tools\php\ShipmentEncoder\src;

include_once __DIR__.'/ShipmentEncoderInterface.php';
include_once __DIR__.'/v0_6_7ShipmentEncoder.php';

class v0_6_10ShipmentEncoder extends v0_6_7ShipmentEncoder {

	public function createShipment(string $proposalCode, ?int $sessionNumber=null, ?string $uuid=null): array {
		if(!empty($this->shipmentMessage)){
			throw new \Exception("Shipment already added to message");
		}
		if(!preg_match('/^[0-9A-Za-z]+$/', $proposalCode)){
			throw new \Exception("Bad proposal code $proposalCode");
		}
		$shipment=$this->getBaseObject('Shipment', $uuid);
		$shipment['proposalCode']=$proposalCode;
		if(!empty($sessionNumber)){
			if($sessionNumber<1){
				throw new \Exception("Session number must be a positive number");
			}
			$shipment['sessionNumber'] = $sessionNumber;
		}
		$this->shipmentMessage=[
			'version'=>$this->getVersion()
		];
		$this->setObjectToMessage($shipment);
		return $shipment;
	}

	/**
	 * Returns an array with the basic "mxlimsType", "version", and "uuid" parameters, generating the UUID if not supplied.
	 * @param string $mxlimsType The type of object.
	 * @param string|null $uuid A pre-existing UUID for the object. If not supplied, one will be generated.
	 * @return array The base object.
	 * @throws \Exception if $mxlimsType is not alphanumeric or does not start with a capital letter
	 */
	public function getBaseObject(string $mxlimsType, ?string $uuid=null): array {
		if(!preg_match('/^[A-Z][a-zA-Z0-9]+$/', $mxlimsType)){
			throw new \Exception("Bad mxlimsType $mxlimsType");
		}
		if(!$uuid){
			$uuid=$this->generateUuid();
		}
		return [
			'mxlimsType' => $mxlimsType,
//			'version' => $this->getVersion(),
			'uuid' => $uuid
		];
	}

}


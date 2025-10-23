#!/usr/bin/env python3
"""
Produtor de voos para o sistema Kafka Airport
Gera dados simulados de voos de chegada e partida
"""

import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
from faker import Faker

class AirportProducer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """Inicializa o produtor Kafka"""
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.fake = Faker('pt_BR')
        
        # Lista de códigos de aeroportos brasileiros
        self.airports = [
            'GRU', 'GIG', 'BSB', 'CGH', 'SDU', 'CNF', 'SSA', 'REC', 'FOR', 'BEL',
            'MAO', 'CWB', 'POA', 'FLN', 'VIT', 'MCZ', 'CGB', 'AJU', 'JPA', 'NAT'
        ]
        
        # Lista de companhias aéreas
        self.airlines = [
            'GOL', 'TAM', 'Azul', 'American Airlines', 'Delta', 'United',
            'Air France', 'Lufthansa', 'British Airways', 'Iberia'
        ]
        
        # Lista de tipos de aeronaves
        self.aircraft_types = [
            'Boeing 737', 'Airbus A320', 'Boeing 777', 'Airbus A330',
            'Boeing 787', 'Embraer E190', 'ATR 72', 'Boeing 767'
        ]

    def generate_flight_data(self, flight_type):
        """Gera dados simulados de voo"""
        flight_number = f"{random.choice(self.airlines)[:2]}{random.randint(1000, 9999)}"
        
        # Determina origem e destino baseado no tipo do voo
        if flight_type == 'chegada':
            origin = random.choice(self.airports)
            destination = 'CGH'  # Aeroporto de Congonhas (base)
        else:  # partida
            origin = 'CGH'
            destination = random.choice(self.airports)
        
        # Gera horário baseado no tipo do voo
        base_time = datetime.now()
        if flight_type == 'chegada':
            # Voos de chegada: próximas 8 horas
            scheduled_time = base_time + timedelta(minutes=random.randint(0, 480))
        else:
            # Voos de partida: próximas 12 horas
            scheduled_time = base_time + timedelta(minutes=random.randint(30, 720))
        
        # Status do voo
        status_options = ['No horário', 'Atrasado', 'Cancelado', 'Embarcando', 'Decolou']
        if flight_type == 'chegada':
            status_options.extend(['Pousou', 'Desembarcando'])
        
        flight_data = {
            'flight_number': flight_number,
            'airline': random.choice(self.airlines),
            'aircraft_type': random.choice(self.aircraft_types),
            'origin': origin,
            'destination': destination,
            'scheduled_time': scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choice(status_options),
            'gate': f"G{random.randint(1, 15)}",
            'terminal': random.choice(['1', '2', '3']),
            'passengers': random.randint(80, 300),
            'flight_type': flight_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Adiciona atraso se o status for "Atrasado"
        if flight_data['status'] == 'Atrasado':
            delay_minutes = random.randint(15, 120)
            actual_time = scheduled_time + timedelta(minutes=delay_minutes)
            flight_data['actual_time'] = actual_time.strftime('%Y-%m-%d %H:%M:%S')
            flight_data['delay_minutes'] = delay_minutes
        
        return flight_data

    def send_flight(self, topic, flight_data):
        """Envia dados do voo para o tópico Kafka"""
        try:
            # Usa o número do voo como chave para particionamento
            key = flight_data['flight_number']
            
            future = self.producer.send(topic, key=key, value=flight_data)
            record_metadata = future.get(timeout=10)
            
            print(f"✈️ Voo enviado para {topic}:")
            print(f"   {flight_data['flight_number']} - {flight_data['origin']} → {flight_data['destination']}")
            print(f"   Status: {flight_data['status']} | Horário: {flight_data['scheduled_time']}")
            print(f"   Partição: {record_metadata.partition} | Offset: {record_metadata.offset}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Erro ao enviar voo: {e}")

    def start_producing(self, interval=5):
        """Inicia a produção contínua de voos"""
        print("🚀 Iniciando produtor de voos do aeroporto...")
        print("📡 Conectado ao Kafka. Gerando voos...")
        print("=" * 80)
        
        try:
            while True:
                # Gera voo de chegada (70% de chance)
                if random.random() < 0.7:
                    arrival_flight = self.generate_flight_data('chegada')
                    self.send_flight('chegada', arrival_flight)
                
                # Gera voo de partida (60% de chance)
                if random.random() < 0.6:
                    departure_flight = self.generate_flight_data('partida')
                    self.send_flight('partida', departure_flight)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Parando produtor de voos...")
        finally:
            self.producer.close()
            print("✅ Produtor encerrado com sucesso!")

if __name__ == "__main__":
    producer = AirportProducer()
    producer.start_producing(interval=3)  # Gera voos a cada 3 segundos

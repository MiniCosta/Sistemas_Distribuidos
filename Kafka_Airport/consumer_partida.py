#!/usr/bin/env python3
"""
Consumidor de voos de partida para o sistema Kafka Airport
"""

import json
from kafka import KafkaConsumer
from datetime import datetime

class DepartureConsumer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """Inicializa o consumidor de partidas"""
        self.consumer = KafkaConsumer(
            'partida',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='partida-consumer-group',
            auto_offset_reset='latest',  # Lê apenas mensagens novas
            enable_auto_commit=True
        )

    def format_flight_info(self, flight_data):
        """Formata informações do voo para exibição"""
        status_emoji = {
            'No horário': '✅',
            'Atrasado': '⚠️',
            'Cancelado': '❌',
            'Embarcando': '🚶‍♂️',
            'Decolou': '🛫'
        }
        
        emoji = status_emoji.get(flight_data['status'], '✈️')
        
        info = f"""
🛫 PARTIDA - {flight_data['flight_number']} {emoji}
   Companhia: {flight_data['airline']}
   Aeronave: {flight_data['aircraft_type']}
   Origem: {flight_data['origin']} → Destino: {flight_data['destination']}
   Horário Programado: {flight_data['scheduled_time']}
   Status: {flight_data['status']}
   Portão: {flight_data['gate']} | Terminal: {flight_data['terminal']}
   Passageiros: {flight_data['passengers']}"""
        
        if 'actual_time' in flight_data:
            info += f"\n   Horário Real: {flight_data['actual_time']}"
            info += f"\n   Atraso: {flight_data['delay_minutes']} minutos"
        
        info += f"\n   Recebido em: {datetime.now().strftime('%H:%M:%S')}"
        
        return info

    def start_consuming(self):
        """Inicia o consumo de mensagens de partida"""
        print("🛫 Iniciando consumidor de PARTIDAS...")
        print("📡 Aguardando voos de partida...")
        print("=" * 80)
        
        try:
            for message in self.consumer:
                flight_data = message.value
                
                print(self.format_flight_info(flight_data))
                print("-" * 80)
                
        except KeyboardInterrupt:
            print("\n🛑 Parando consumidor de partidas...")
        finally:
            self.consumer.close()
            print("✅ Consumidor de partidas encerrado!")

if __name__ == "__main__":
    consumer = DepartureConsumer()
    consumer.start_consuming()

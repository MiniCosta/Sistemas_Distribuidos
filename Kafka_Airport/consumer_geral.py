#!/usr/bin/env python3
"""
Consumidor geral que monitora todos os voos (chegada e partida)
"""

import json
from kafka import KafkaConsumer
from datetime import datetime

class GeneralConsumer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """Inicializa o consumidor geral"""
        self.consumer = KafkaConsumer(
            'chegada', 'partida',  # Consome de ambos os tópicos
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='general-consumer-group',
            auto_offset_reset='latest',
            enable_auto_commit=True
        )

    def format_flight_info(self, flight_data, topic):
        """Formata informações do voo para exibição"""
        flight_type = "🛬 CHEGADA" if topic == 'chegada' else "🛫 PARTIDA"
        
        status_emoji = {
            'No horário': '✅',
            'Atrasado': '⚠️',
            'Cancelado': '❌',
            'Embarcando': '🚶‍♂️',
            'Decolou': '🛫',
            'Pousou': '🛬',
            'Desembarcando': '👥'
        }
        
        emoji = status_emoji.get(flight_data['status'], '✈️')
        
        info = f"""
{flight_type} - {flight_data['flight_number']} {emoji}
   {flight_data['airline']} | {flight_data['aircraft_type']}
   {flight_data['origin']} → {flight_data['destination']}
   Programado: {flight_data['scheduled_time']} | Status: {flight_data['status']}
   Gate: {flight_data['gate']} | Terminal: {flight_data['terminal']} | Passageiros: {flight_data['passengers']}"""
        
        if 'actual_time' in flight_data:
            info += f"\n   Real: {flight_data['actual_time']} (Atraso: {flight_data['delay_minutes']}min)"
        
        return info

    def start_consuming(self):
        """Inicia o consumo de mensagens de todos os tópicos"""
        print("🌐 Iniciando MONITOR GERAL do aeroporto...")
        print("📡 Monitorando todos os voos (chegadas e partidas)...")
        print("=" * 80)
        
        try:
            for message in self.consumer:
                flight_data = message.value
                topic = message.topic
                
                print(self.format_flight_info(flight_data, topic))
                print(f"   Tópico: {topic} | Partição: {message.partition} | Offset: {message.offset}")
                print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 80)
                
        except KeyboardInterrupt:
            print("\n🛑 Parando monitor geral...")
        finally:
            self.consumer.close()
            print("✅ Monitor geral encerrado!")

if __name__ == "__main__":
    consumer = GeneralConsumer()
    consumer.start_consuming()

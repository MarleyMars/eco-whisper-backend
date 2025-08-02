-- Eco Whisper Demo Sample Data
-- This file contains INSERT statements to recreate the existing data

-- Insert sample users
INSERT OR REPLACE INTO users (user_id, username, email) VALUES
('user1', 'demo_user', 'demo@example.com'),
('user2', 'eco_friendly', 'eco@example.com');

-- Insert Intent data
INSERT OR REPLACE INTO Intent (intent_id, name, description, requires_data_access, response_template, question_patterns) VALUES
('intent1', 'query_electricity_today', 'how much electricity did I use today', 1, 'You used {kwh} kilowatt-hours today, which cost about {cost} euros.', '["how much electricity did I use today", "what is my electricity usage today", "how much power did I use today", "electricity usage today"]'),
('intent2', 'query_community_usage', 'how much did my community use today', 1, 'Your community used an average of {avg_kwh} kilowatt-hours per person today.', '["how much did my community use today", "community electricity usage", "neighborhood power consumption", "how much did my community use today", "community usage today"]'),
('intent3', 'compare_yesterday', 'am I using more or less than yesterday', 1, 'You used {compare} electricity today, {diff} kilowatt-hours {compare_text}.', '["am I using more or less than yesterday", "compare today vs yesterday", "electricity usage comparison"]'),
('intent4', 'greenest_time', 'what is the greenest time to use power', 0, 'The greenest time to use electricity is {green_time}.', '["what is the greenest time to use power", "best time to use electricity", "greenest time for power", "greenest time to use power", "when is the best time to use electricity"]'),
('intent5', 'query_co2_saved', 'how much carbon dioxide did I save today', 1, 'You saved {co2} kilograms of carbon dioxide today.', '["how much carbon dioxide did I save today", "carbon dioxide saved", "environmental impact today", "how much CO₂ did I save today", "co2 saved today", "carbon saved today"]'),
('intent6', 'random_tip', 'give me a sustainability tip', 1, 'Here is a tip: {tip}', '["give me a sustainability tip", "eco tip", "green advice", "sustainability tip", "sustainable tip", "eco-friendly tip", "give me a sustainability tip"]'),
('intent7', 'query_water_saved', 'how much water did I save', 1, 'You saved {water} liters of water today.', '["how much water did I save", "water conservation", "water usage saved"]'),
('intent8', 'query_money_saved_week', 'how much money did I save this week', 1, 'You saved {money} euros this week.', '["how much money did I save this week", "weekly savings", "cost savings this week"]'),
('intent9', 'compare_community', 'how green am I compared to others', 1, 'You used {compare} electricity than your community average, {diff} kilowatt-hours {compare_text}.', '["how green am I compared to others", "community comparison", "am I greener than others", "how green am I compared to others", "green compared to others", "how green am I compared to others"]'),
('intent10', 'summary_today', 'summarize my green behavior today', 1, 'Today you used {kwh} kilowatt-hours and saved {co2} kilograms of CO2.', '["summarize my green behavior today", "today summary", "daily eco summary", "green behavior today", "eco behavior summary"]');

-- Insert sample electricity usage data
INSERT OR REPLACE INTO Electricity_Usage (usage_id, user_id, date, kwh_used, estimated_cost, is_peak_time) VALUES
('usage1', 'user1', '2025-01-23', 5.6, 2.08, 0),
('usage2', 'user1', '2025-01-22', 6.2, 2.31, 1),
('usage3', 'user2', '2025-01-23', 4.8, 1.79, 0),
('usage4', 'user2', '2025-01-22', 5.1, 1.90, 0);

-- Insert community statistics
INSERT OR REPLACE INTO Community_Stats (stat_id, community_id, date, avg_kwh_per_user, total_co2_saved) VALUES
('stat1', 'community1', '2025-01-23', 5.2, 1.8),
('stat2', 'community1', '2025-01-22', 5.7, 1.5),
('stat3', 'community1', '2025-01-21', 5.9, 1.2);

-- Insert impact records
INSERT OR REPLACE INTO Impact_Record (impact_id, user_id, date, impact_value, impact_unit, impact_equivalent, impact_type) VALUES
('impact1', 'user1', '2025-01-23', 2.1, 'kg', 'equivalent to planting 0.1 trees', 'CO2_saved'),
('impact2', 'user1', '2025-01-23', 15.0, 'liters', 'equivalent to 1 shower', 'water_saved'),
('impact3', 'user2', '2025-01-23', 2.8, 'kg', 'equivalent to planting 0.15 trees', 'CO2_saved'),
('impact4', 'user2', '2025-01-23', 20.0, 'liters', 'equivalent to 1.3 showers', 'water_saved');

-- Insert tips
INSERT OR REPLACE INTO Tip (tip_id, content, category, impact_value) VALUES
('tip1', 'Turn off lights when leaving a room to save 0.5 kWh per day', 'electricity', 0.5),
('tip2', 'Use electricity during off-peak hours', 'green_time', 0.2),
('tip3', 'Wash clothes with cold water to save 90% of energy', 'laundry', 1.2),
('tip4', 'Use a reusable water bottle instead of disposable plastic', 'plastic', 0.0),
('tip5', 'Run dishwasher only when full to save 0.8 kWh per load', 'appliance', 0.8);

-- Insert sample smart meters
INSERT OR REPLACE INTO smart_meters (meter_id, user_id, location, installation_date, is_active) VALUES
('meter1', 'user1', 'Kitchen', '2025-01-01 00:00:00', 1),
('meter2', 'user1', 'Living Room', '2025-01-01 00:00:00', 1),
('meter3', 'user2', 'Kitchen', '2025-01-01 00:00:00', 1);

-- Insert appliance usage data
INSERT OR REPLACE INTO appliance_usage (meter_id, appliance_name, start_time, end_time, kwh_consumed) VALUES
('meter1', 'Dishwasher', '2025-01-23 20:00:00', '2025-01-23 21:30:00', 1.2),
('meter2', 'TV', '2025-01-23 19:00:00', '2025-01-23 22:00:00', 0.8),
('meter3', 'Washing Machine', '2025-01-23 18:00:00', '2025-01-23 19:30:00', 1.5);

-- Insert electricity rates
INSERT OR REPLACE INTO electricity_rates (rate_type, rate_per_kwh, start_time, end_time, effective_date) VALUES
('peak', 0.45, '06:00:00', '22:00:00', '2025-01-01'),
('off_peak', 0.35, '22:00:00', '06:00:00', '2025-01-01'),
('standard', 0.40, NULL, NULL, '2025-01-01');

-- Insert sample conversations (if any exist)
-- Note: These are sample conversations, actual data would come from the existing database
INSERT OR REPLACE INTO conversations (conversation_id, user_id, user_message, assistant_message, intent_matched) VALUES
('conv1', 'user1', 'How much electricity did I use today?', 'You used 5.6 kilowatt-hours today, which cost about 2.45 dollars.', 'intent1'),
('conv2', 'user1', 'Give me a sustainability tip', 'Here is a tip: Turn off lights when leaving a room to save 0.5 kWh per day', 'intent6'),
('conv3', 'user2', 'How much did my community use today?', 'Your community used an average of 5.2 kilowatt-hours per person today.', 'intent2'); 
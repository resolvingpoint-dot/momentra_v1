INSERT INTO personal_moment_types (
																    moment_type_code,
																    moment_type_name,
																    description,
																    display_order,
																    is_active
																)
																VALUES
																(
																    'LIFE_OPERATIONS',
																    'Life Operations',
																    'Stability intelligence for daily life, pressure, recovery, mood, money, and rhythm.',
																    1,
																    TRUE
																),
																(
																    'FUTURE_BUILDING',
																    'Future Building',
																    'Growth intelligence for progress, milestones, opportunity, learning, investment, and direction.',
																    2,
																    TRUE
																),
																(
																    'LIFESTYLE',
																    'Lifestyle',
																    'Fulfillment intelligence for experiences, wellbeing, creativity, exploration, and lifestyle ROI.',
																    3,
																    TRUE
																),
																(
																    'RELATIONSHIPS',
																    'Relationships',
																    'Connection intelligence for time, support, shared experiences, relationship investment, and trust.',
																    4,
																    TRUE
																)
																ON CONFLICT (moment_type_code) DO UPDATE
																SET
																    moment_type_name = EXCLUDED.moment_type_name,
																    description = EXCLUDED.description,
																    display_order = EXCLUDED.display_order,
																    is_active = EXCLUDED.is_active,
																    updated_at = CURRENT_TIMESTAMP;
-- >>>STMT<<<
INSERT INTO personal_categories (
    user_id,
    moment_type_code,
    category_group,
    category_code,
    category_name,
    display_order,
    is_money_category,
    is_active
)
VALUES
-- Life Operations money categories
(NULL, 'LIFE_OPERATIONS', 'Money', 'ESSENTIALS', 'Essentials', 1, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'RENT', 'Rent', 2, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'FOOD', 'Food', 3, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'TRANSPORT', 'Transport', 4, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'UTILITIES', 'Utilities', 5, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'HEALTH', 'Health', 6, TRUE, TRUE),
(NULL, 'LIFE_OPERATIONS', 'Money', 'OTHER', 'Other', 99, TRUE, TRUE),

-- Future Building investment categories
(NULL, 'FUTURE_BUILDING', 'Investment', 'COURSE', 'Course', 1, TRUE, TRUE),
(NULL, 'FUTURE_BUILDING', 'Investment', 'CERTIFICATION', 'Certification', 2, TRUE, TRUE),
(NULL, 'FUTURE_BUILDING', 'Investment', 'TOOLS', 'Tools', 3, TRUE, TRUE),
(NULL, 'FUTURE_BUILDING', 'Investment', 'NETWORKING', 'Networking', 4, TRUE, TRUE),
(NULL, 'FUTURE_BUILDING', 'Investment', 'BUSINESS', 'Business', 5, TRUE, TRUE),
(NULL, 'FUTURE_BUILDING', 'Investment', 'OTHER', 'Other', 99, TRUE, TRUE),

-- Lifestyle spend categories
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'TRAVEL', 'Travel', 1, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'FOOD_DINING', 'Food & Dining', 2, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'ENTERTAINMENT', 'Entertainment', 3, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'WELLBEING', 'Wellbeing', 4, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'FITNESS', 'Fitness', 5, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'LEARNING', 'Learning', 6, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'SHOPPING', 'Shopping', 7, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'HOBBIES', 'Hobbies', 8, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'EXPERIENCES', 'Experiences', 9, TRUE, TRUE),
(NULL, 'LIFESTYLE', 'Lifestyle Spend', 'OTHER', 'Other', 99, TRUE, TRUE),

-- Relationship spend categories
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'DINING', 'Dining', 1, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'TRAVEL', 'Travel', 2, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'GIFT', 'Gift', 3, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'EVENT', 'Event', 4, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'SUPPORT', 'Support', 5, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'EXPERIENCE', 'Experience', 6, TRUE, TRUE),
(NULL, 'RELATIONSHIPS', 'Relationship Spend', 'OTHER', 'Other', 99, TRUE, TRUE)
ON CONFLICT DO NOTHING;
-- >>>STMT<<<
UPDATE personal_memory_patterns
																SET
																    pattern_confidence_pct = confidence_score,
																    pattern_explanation = pattern_description
																WHERE pattern_confidence_pct IS NULL;
-- >>>STMT<<<
INSERT INTO group_moment_profiles
																(moment_type, profile_code, profile_name, profile_description, display_order)
																VALUES
																('SHARED_EXPERIENCE','TRIP_VACATION','Trip / Vacation','Travel, vacations and shared journeys.',1),
																('SHARED_EXPERIENCE','WEDDING','Wedding','Ceremonies, vendors, guests and celebrations.',2),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','Celebration / Party','Birthdays, parties and social celebrations.',3),
																('SHARED_EXPERIENCE','OFFICE_OUTING','Office Outing','Team outings and workplace experiences.',4),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','Community Event','Community gatherings and public participation.',5),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','Custom Experience','Create a custom shared experience.',6),
																
																('SHARED_PURCHASE','GIFT_POOL','Gift Pool','Collect money and decide on a gift.',1),
																('SHARED_PURCHASE','GROUP_PURCHASE','Group Purchase','Buy something together.',2),
																('SHARED_PURCHASE','SHARED_ASSET','Shared Asset','Own and manage something together.',3),
																('SHARED_PURCHASE','FAMILY_PURCHASE','Family Purchase','Coordinate family purchases.',4),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','Community Purchase','Coordinate purchases for a community.',5),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','Custom Purchase','Create a custom shared purchase.',6),
																
																('SHARED_LIVING','FLATMATES','Flatmates','Friends sharing a home.',1),
																('SHARED_LIVING','FAMILY_HOUSEHOLD','Family Household','Family members managing a home.',2),
																('SHARED_LIVING','CO_LIVING','Co-Living','Modern shared accommodation.',3),
																('SHARED_LIVING','SHARED_RENTAL','Shared Rental','Temporary shared housing.',4),
																('SHARED_LIVING','COMMUNITY_LIVING','Community Living','Hostels, dorms, societies and shared residences.',5),
																('SHARED_LIVING','CUSTOM_LIVING','Custom Living','Create a custom shared living setup.',6);
-- >>>STMT<<<
INSERT INTO group_moment_roles
																(role_code, moment_type, role_name, role_description, permission_json, display_order, is_default)
																VALUES
																('ORGANIZER','ALL','Organizer','Can manage setup, members and records.','{"can_edit":true,"can_delete":true,"can_invite":true}'::jsonb,1,false),
																('CO_ORGANIZER','ALL','Co-Organizer','Can help manage the moment.','{"can_edit":true,"can_delete":false,"can_invite":true}'::jsonb,2,false),
																('PARTICIPANT','ALL','Participant','Can participate and add updates.','{"can_edit_own":true,"can_delete_own":true}'::jsonb,3,true),
																('VIEWER','ALL','Viewer','Can only view activity.','{"can_view":true}'::jsonb,4,false),
																('HOUSEHOLD_LEAD','SHARED_LIVING','Household Lead','Primary coordinator for shared living.','{"can_edit":true,"can_invite":true,"can_manage_rules":true}'::jsonb,5,false),
																('CONTRIBUTOR','SHARED_PURCHASE','Contributor','Contributes toward a purchase.','{"can_contribute":true,"can_vote":true}'::jsonb,6,false);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','TRIP_VACATION','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','TRIP_VACATION','BOOKING','Booking',2),
																('SHARED_EXPERIENCE','TRIP_VACATION','PLANNING_ITEM','Planning Item',3),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','Expense',4),
																('SHARED_EXPERIENCE','TRIP_VACATION','MEMORY','Memory',5),
																('SHARED_EXPERIENCE','TRIP_VACATION','POLL','Poll',6);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','WEDDING','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','Vendor',2),
																('SHARED_EXPERIENCE','WEDDING','EXPENSE','Expense',3),
																('SHARED_EXPERIENCE','WEDDING','CONTRIBUTION','Contribution',4),
																('SHARED_EXPERIENCE','WEDDING','ATTENDANCE','Attendance',5),
																('SHARED_EXPERIENCE','WEDDING','MEMORY','Memory',6),
																('SHARED_EXPERIENCE','WEDDING','POLL','Poll',7);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','PLANNING_ITEM','Planning Item',2),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','EXPENSE','Expense',3),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','ATTENDANCE','Attendance',4),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','MEMORY','Memory',5),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','POLL','Poll',6);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','OFFICE_OUTING','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','OFFICE_OUTING','PLANNING_ITEM','Planning Item',2),
																('SHARED_EXPERIENCE','OFFICE_OUTING','ATTENDANCE','Attendance',3),
																('SHARED_EXPERIENCE','OFFICE_OUTING','UPDATE','Update',4),
																('SHARED_EXPERIENCE','OFFICE_OUTING','EXPENSE','Expense',5),
																('SHARED_EXPERIENCE','OFFICE_OUTING','MEMORY','Memory',6),
																('SHARED_EXPERIENCE','OFFICE_OUTING','POLL','Poll',7);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','VENDOR','Vendor',2),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','CONTRIBUTION','Contribution',3),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','ATTENDANCE','Attendance',4),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','UPDATE','Update',5),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','EXPENSE','Expense',6),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','MEMORY','Memory',7),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','POLL','Poll',8);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','PARTICIPANT','Participant',1),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','PLANNING_ITEM','Planning Item',2),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','BOOKING','Booking',3),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','EXPENSE','Expense',4),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','CONTRIBUTION','Contribution',5),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','VENDOR','Vendor',6),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','ATTENDANCE','Attendance',7),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','UPDATE','Update',8),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','MEMORY','Memory',9),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','POLL','Poll',10);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_PURCHASE','GIFT_POOL','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','GIFT_POOL','CONTRIBUTION','Contribution',2),
																('SHARED_PURCHASE','GIFT_POOL','PURCHASE_ITEM','Purchase Item',3),
																('SHARED_PURCHASE','GIFT_POOL','POLL','Poll',4),
																('SHARED_PURCHASE','GIFT_POOL','UPDATE','Update',5),
																('SHARED_PURCHASE','GIFT_POOL','DELIVERY_HANDOVER','Delivery / Handover',6),
																('SHARED_PURCHASE','GIFT_POOL','MEMORY','Memory',7),
																
																('SHARED_PURCHASE','GROUP_PURCHASE','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','GROUP_PURCHASE','CONTRIBUTION','Contribution',2),
																('SHARED_PURCHASE','GROUP_PURCHASE','PURCHASE_ITEM','Purchase Item',3),
																('SHARED_PURCHASE','GROUP_PURCHASE','VENDOR','Vendor',4),
																('SHARED_PURCHASE','GROUP_PURCHASE','EXPENSE','Expense',5),
																('SHARED_PURCHASE','GROUP_PURCHASE','POLL','Poll',6),
																('SHARED_PURCHASE','GROUP_PURCHASE','UPDATE','Update',7),
																('SHARED_PURCHASE','GROUP_PURCHASE','DELIVERY_HANDOVER','Delivery / Handover',8),
																
																('SHARED_PURCHASE','SHARED_ASSET','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','SHARED_ASSET','CONTRIBUTION','Contribution',2),
																('SHARED_PURCHASE','SHARED_ASSET','PURCHASE_ITEM','Purchase Item',3),
																('SHARED_PURCHASE','SHARED_ASSET','VENDOR','Vendor',4),
																('SHARED_PURCHASE','SHARED_ASSET','EXPENSE','Expense',5),
																('SHARED_PURCHASE','SHARED_ASSET','POLL','Poll',6),
																('SHARED_PURCHASE','SHARED_ASSET','OWNERSHIP','Ownership',7),
																('SHARED_PURCHASE','SHARED_ASSET','DELIVERY_HANDOVER','Delivery / Handover',8),
																
																('SHARED_PURCHASE','FAMILY_PURCHASE','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','FAMILY_PURCHASE','PURCHASE_ITEM','Purchase Item',2),
																('SHARED_PURCHASE','FAMILY_PURCHASE','VENDOR','Vendor',3),
																('SHARED_PURCHASE','FAMILY_PURCHASE','EXPENSE','Expense',4),
																('SHARED_PURCHASE','FAMILY_PURCHASE','UPDATE','Update',5),
																('SHARED_PURCHASE','FAMILY_PURCHASE','DELIVERY_HANDOVER','Delivery / Handover',6),
																
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','CONTRIBUTION','Contribution',2),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','PURCHASE_ITEM','Purchase Item',3),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','VENDOR','Vendor',4),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','EXPENSE','Expense',5),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','POLL','Poll',6),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','UPDATE','Update',7),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','OWNERSHIP','Ownership',8),
																('SHARED_PURCHASE','COMMUNITY_PURCHASE','DELIVERY_HANDOVER','Delivery / Handover',9);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																VALUES
																('SHARED_PURCHASE','CUSTOM_PURCHASE','CONTRIBUTOR','Contributor',1),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','CONTRIBUTION','Contribution',2),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','PURCHASE_ITEM','Purchase Item',3),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','VENDOR','Vendor',4),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','EXPENSE','Expense',5),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','POLL','Poll',6),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','UPDATE','Update',7),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','OWNERSHIP','Ownership',8),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','DELIVERY_HANDOVER','Delivery / Handover',9),
																('SHARED_PURCHASE','CUSTOM_PURCHASE','MEMORY','Memory',10);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order)
																SELECT
																    'SHARED_LIVING',
																    profile_code,
																    module_code,
																    module_label,
																    display_order
																FROM (
																    VALUES
																    ('RESIDENT','Resident',1),
																    ('EXPENSE','Expense',2),
																    ('CONTRIBUTION','Contribution',3),
																    ('TASK','Task',4),
																    ('ASSET','Asset',5),
																    ('RULE','Rule',6),
																    ('MAINTENANCE','Maintenance',7),
																    ('UPDATE','Update',8),
																    ('POLL','Poll',9),
																    ('MEMORY','Memory',10)
																) AS modules(module_code, module_label, display_order)
																CROSS JOIN (
																    VALUES
																    ('FLATMATES'),
																    ('FAMILY_HOUSEHOLD'),
																    ('CO_LIVING'),
																    ('SHARED_RENTAL'),
																    ('COMMUNITY_LIVING'),
																    ('CUSTOM_LIVING')
																) AS profiles(profile_code);
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category)
																VALUES
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','RENT','Rent',1,true),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','GROCERIES','Groceries',2,true),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','UTILITIES','Utilities',3,true),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','INTERNET','Internet',4,true),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','CLEANING','Cleaning',5,true),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','ELECTRICITY','Electricity',6,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','WATER','Water',7,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','GAS','Gas',8,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','MAINTENANCE','Maintenance',9,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','FURNITURE','Furniture',10,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','APPLIANCES','Appliances',11,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','HOUSEHOLD_SUPPLIES','Household Supplies',12,false),
																('SHARED_LIVING','ALL','EXPENSE','CATEGORY','MISCELLANEOUS','Miscellaneous',99,false);
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category)
																VALUES
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','HOTEL','Hotel',1,true),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','FOOD','Food',2,true),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','TRANSPORT','Transport',3,true),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','ACTIVITY','Activity',4,true),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','FLIGHT','Flight',5,false),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','FUEL','Fuel',6,false),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','SHOPPING','Shopping',7,false),
																('SHARED_EXPERIENCE','TRIP_VACATION','EXPENSE','CATEGORY','MISCELLANEOUS','Miscellaneous',99,false);
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category)
																VALUES
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','VENUE','Venue',1,true),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','CATERING','Catering',2,true),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','PHOTOGRAPHY','Photography',3,true),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','DECORATION','Decoration',4,true),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','MAKEUP','Makeup',5,false),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','INVITATION','Invitation',6,false),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','MUSIC','Music',7,false),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','ENTERTAINMENT','Entertainment',8,false),
																('SHARED_EXPERIENCE','WEDDING','VENDOR','CATEGORY','OTHER','Other',99,false);
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category)
																VALUES
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','ELECTRONICS','Electronics',1,true),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','FURNITURE','Furniture',2,true),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','APPLIANCE','Appliance',3,true),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','GIFT','Gift',4,true),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','VEHICLE','Vehicle',5,false),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','HOME_IMPROVEMENT','Home Improvement',6,false),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','COMMUNITY_INFRASTRUCTURE','Community Infrastructure',7,false),
																('SHARED_PURCHASE','ALL','PURCHASE_ITEM','CATEGORY','OTHER','Other',99,false);
-- >>>STMT<<<
INSERT INTO group_moment_profiles
																(moment_type, profile_code, profile_name, profile_description, display_order)
																VALUES
																('SHARED_GOAL','SAVINGS_GOAL','Savings Goal','Group goal to save or collect money together.',1),
																('SHARED_GOAL','TRAVEL_GOAL','Travel Goal','Group goal for a future trip or experience.',2),
																('SHARED_GOAL','PURCHASE_GOAL','Purchase Goal','Group goal for buying something together.',3),
																('SHARED_GOAL','FITNESS_GOAL','Fitness Goal','Group goal around health or fitness progress.',4),
																('SHARED_GOAL','LEARNING_GOAL','Learning Goal','Group goal around learning or skill building.',5),
																('SHARED_GOAL','CUSTOM_GOAL','Custom Goal','Create a custom shared goal.',6),
																
																('COMMUNITY_COORDINATION','APARTMENT_COMMUNITY','Apartment Community','Coordinate residents, events, issues and decisions.',1),
																('COMMUNITY_COORDINATION','RWA_ASSOCIATION','RWA Association','Resident welfare association coordination.',2),
																('COMMUNITY_COORDINATION','CLUB_GROUP','Club / Interest Group','Coordinate club members and group activities.',3),
																('COMMUNITY_COORDINATION','VOLUNTEER_GROUP','Volunteer Group','Coordinate volunteers, events and community work.',4),
																('COMMUNITY_COORDINATION','FAMILY_COMMUNITY','Family Community','Coordinate extended family events and responsibilities.',5),
																('COMMUNITY_COORDINATION','CUSTOM_COMMUNITY','Custom Community','Create a custom community coordination moment.',6)
																ON CONFLICT (moment_type, profile_code) DO NOTHING;
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order, quick_add_category, moment_type_support)
																VALUES
																('SHARED_EXPERIENCE','TRIP_VACATION','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE'),
																('SHARED_EXPERIENCE','WEDDING','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE'),
																('SHARED_EXPERIENCE','CELEBRATION_PARTY','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE'),
																('SHARED_EXPERIENCE','OFFICE_OUTING','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE'),
																('SHARED_EXPERIENCE','COMMUNITY_EVENT','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE'),
																('SHARED_EXPERIENCE','CUSTOM_EXPERIENCE','BUDGET','Budget',1,'MONEY','SHARED_EXPERIENCE');
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order, quick_add_category, moment_type_support)
																SELECT
																    'SHARED_GOAL',
																    profile_code,
																    module_code,
																    module_label,
																    display_order,
																    quick_add_category,
																    'SHARED_GOAL'
																FROM (
																    VALUES
																    ('CONTRIBUTION','Contribution',1,'MONEY'),
																    ('MILESTONE','Milestone',2,'OPERATIONS'),
																    ('PROGRESS_UPDATE','Progress Update',3,'OPERATIONS'),
																    ('TASK','Task',4,'OPERATIONS'),
																    ('RESOURCE','Resource',5,'ASSETS'),
																    ('POLL','Poll',6,'GOVERNANCE'),
																    ('MEMORY','Memory',7,'MEMORY')
																) AS modules(module_code, module_label, display_order, quick_add_category)
																CROSS JOIN (
																    VALUES
																    ('SAVINGS_GOAL'),
																    ('TRAVEL_GOAL'),
																    ('PURCHASE_GOAL'),
																    ('FITNESS_GOAL'),
																    ('LEARNING_GOAL'),
																    ('CUSTOM_GOAL')
																) AS profiles(profile_code);
-- >>>STMT<<<
INSERT INTO group_quick_add_config
																(moment_type, moment_profile, module_code, module_label, display_order, quick_add_category, moment_type_support)
																SELECT
																    'COMMUNITY_COORDINATION',
																    profile_code,
																    module_code,
																    module_label,
																    display_order,
																    quick_add_category,
																    'COMMUNITY_COORDINATION'
																FROM (
																    VALUES
																    ('MEMBER','Member',1,'PEOPLE'),
																    ('EVENT','Event',2,'OPERATIONS'),
																    ('ISSUE','Issue',3,'OPERATIONS'),
																    ('TASK','Task',4,'OPERATIONS'),
																    ('ANNOUNCEMENT','Announcement',5,'COMMUNICATION'),
																    ('RESOURCE','Resource',6,'ASSETS'),
																    ('VOTE','Vote',7,'GOVERNANCE'),
																    ('APPROVAL','Approval',8,'GOVERNANCE'),
																    ('CONTRIBUTION','Contribution',9,'MONEY'),
																    ('MEMORY','Memory',10,'MEMORY')
																) AS modules(module_code, module_label, display_order, quick_add_category)
																CROSS JOIN (
																    VALUES
																    ('APARTMENT_COMMUNITY'),
																    ('RWA_ASSOCIATION'),
																    ('CLUB_GROUP'),
																    ('VOLUNTEER_GROUP'),
																    ('FAMILY_COMMUNITY'),
																    ('CUSTOM_COMMUNITY')
																) AS profiles(profile_code);
-- >>>STMT<<<
INSERT INTO budget_master_categories
																(category_code, category_name, icon_name, display_order, is_active)
																VALUES
																('TRANSPORT','Travel & Transport','car',1,true),
																('STAY','Stay & Accommodation','bed',2,true),
																('FOOD','Food & Beverages','utensils',3,true),
																('VENUE','Venue & Space','building',4,true),
																('ACTIVITIES','Activities & Entertainment','ticket',5,true),
																('DECOR','Decorations & Setup','sparkles',6,true),
																('GIFTS','Gifts & Ceremonial','gift',7,true),
																('EQUIPMENT','Equipment & Rentals','speaker',8,true),
																('MARKETING','Marketing & Promotion','megaphone',9,true),
																('STAFFING','Volunteers & Staffing','users',10,true),
																('PERMITS','Administration & Permits','file-check',11,true),
																('SHOPPING','Shopping','shopping-bag',12,true),
																('BUFFER','Buffer & Contingency','shield',99,true),
																('CUSTOM','Custom Category','plus-circle',100,true)
																ON CONFLICT (category_code) DO NOTHING;
-- >>>STMT<<<
INSERT INTO experience_budget_templates
																(experience_subtype, category_id, suggested_percentage, display_order, is_default)
																SELECT 'TRIP_VACATION', category_id, pct, ord, true
																FROM (
																    VALUES
																    ('STAY',40,1),
																    ('TRANSPORT',25,2),
																    ('FOOD',15,3),
																    ('ACTIVITIES',10,4),
																    ('BUFFER',10,5)
																) v(code,pct,ord)
																JOIN budget_master_categories b ON b.category_code = v.code;
-- >>>STMT<<<
INSERT INTO experience_budget_templates
																(experience_subtype, category_id, suggested_percentage, display_order, is_default)
																SELECT 'WEDDING', category_id, pct, ord, true
																FROM (
																    VALUES
																    ('VENUE',25,1),
																    ('FOOD',35,2),
																    ('DECOR',15,3),
																    ('GIFTS',5,4),
																    ('EQUIPMENT',10,5),
																    ('BUFFER',10,6)
																) v(code,pct,ord)
																JOIN budget_master_categories b ON b.category_code = v.code;
-- >>>STMT<<<
INSERT INTO experience_budget_templates
																(experience_subtype, category_id, suggested_percentage, display_order, is_default)
																SELECT 'CELEBRATION_PARTY', category_id, pct, ord, true
																FROM (
																    VALUES
																    ('VENUE',20,1),
																    ('FOOD',35,2),
																    ('DECOR',15,3),
																    ('ACTIVITIES',15,4),
																    ('GIFTS',5,5),
																    ('BUFFER',10,6)
																) v(code,pct,ord)
																JOIN budget_master_categories b ON b.category_code = v.code;
-- >>>STMT<<<
INSERT INTO experience_budget_templates
																(experience_subtype, category_id, suggested_percentage, display_order, is_default)
																SELECT 'OFFICE_OUTING', category_id, pct, ord, true
																FROM (
																    VALUES
																    ('TRANSPORT',20,1),
																    ('VENUE',20,2),
																    ('FOOD',25,3),
																    ('ACTIVITIES',25,4),
																    ('EQUIPMENT',5,5),
																    ('BUFFER',5,6)
																) v(code,pct,ord)
																JOIN budget_master_categories b ON b.category_code = v.code;
-- >>>STMT<<<
INSERT INTO experience_budget_templates
																(experience_subtype, category_id, suggested_percentage, display_order, is_default)
																SELECT 'COMMUNITY_EVENT', category_id, pct, ord, true
																FROM (
																    VALUES
																    ('VENUE',20,1),
																    ('FOOD',20,2),
																    ('EQUIPMENT',15,3),
																    ('MARKETING',10,4),
																    ('STAFFING',15,5),
																    ('PERMITS',10,6),
																    ('BUFFER',10,7)
																) v(code,pct,ord)
																JOIN budget_master_categories b ON b.category_code = v.code;
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category, value_group)
																VALUES
																('SHARED_EXPERIENCE','ALL','SETUP','EXPERIENCE_SUBTYPE','TRIP_VACATION','Trip / Vacation',1,true,'EXPERIENCE_SUBTYPE'),
																('SHARED_EXPERIENCE','ALL','SETUP','EXPERIENCE_SUBTYPE','WEDDING','Wedding',2,true,'EXPERIENCE_SUBTYPE'),
																('SHARED_EXPERIENCE','ALL','SETUP','EXPERIENCE_SUBTYPE','CELEBRATION_PARTY','Celebration / Party',3,true,'EXPERIENCE_SUBTYPE'),
																('SHARED_EXPERIENCE','ALL','SETUP','EXPERIENCE_SUBTYPE','OFFICE_OUTING','Office Outing',4,true,'EXPERIENCE_SUBTYPE'),
																('SHARED_EXPERIENCE','ALL','SETUP','EXPERIENCE_SUBTYPE','COMMUNITY_EVENT','Community Event',5,true,'EXPERIENCE_SUBTYPE'),
																('SHARED_EXPERIENCE','ALL','SETUP','PLANNING_MODE','PLAN_NOW','Plan Now',1,true,'PLANNING_MODE'),
																('SHARED_EXPERIENCE','ALL','SETUP','PLANNING_MODE','FUTURE_PLAN','Future Plan',2,true,'PLANNING_MODE');
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category, value_group)
																VALUES
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','SAVINGS','Savings',1,true,'GOAL_TYPE'),
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','TRAVEL','Travel',2,true,'GOAL_TYPE'),
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','PURCHASE','Purchase',3,true,'GOAL_TYPE'),
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','FITNESS','Fitness',4,true,'GOAL_TYPE'),
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','LEARNING','Learning',5,true,'GOAL_TYPE'),
																('SHARED_GOAL','ALL','SETUP','GOAL_TYPE','CUSTOM','Custom',99,false,'GOAL_TYPE'),
																
																('SHARED_GOAL','ALL','MILESTONE','CATEGORY','TARGET_PROGRESS','Target Progress',1,true,'WORK_ITEM_TYPE'),
																('SHARED_GOAL','ALL','MILESTONE','CATEGORY','PAYMENT_MILESTONE','Payment Milestone',2,true,'WORK_ITEM_TYPE'),
																('SHARED_GOAL','ALL','MILESTONE','CATEGORY','TASK_MILESTONE','Task Milestone',3,true,'WORK_ITEM_TYPE'),
																('SHARED_GOAL','ALL','PROGRESS_UPDATE','CATEGORY','GENERAL_UPDATE','General Update',1,true,'WORK_ITEM_TYPE'),
																('SHARED_GOAL','ALL','RESOURCE','CATEGORY','DOCUMENT','Document',1,true,'RESOURCE_TYPE'),
																('SHARED_GOAL','ALL','RESOURCE','CATEGORY','TOOL','Tool',2,true,'RESOURCE_TYPE');
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category, value_group)
																VALUES
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','APARTMENT','Apartment Community',1,true,'COMMUNITY_TYPE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','RWA','RWA Association',2,true,'COMMUNITY_TYPE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','CLUB','Club / Interest Group',3,true,'COMMUNITY_TYPE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','VOLUNTEER','Volunteer Group',4,true,'COMMUNITY_TYPE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','FAMILY','Family Community',5,true,'COMMUNITY_TYPE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COMMUNITY_TYPE','CUSTOM','Custom Community',99,false,'COMMUNITY_TYPE'),
																
																('COMMUNITY_COORDINATION','ALL','SETUP','COORDINATION_MODE','VOTING','Voting',1,true,'COORDINATION_MODE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COORDINATION_MODE','ADMIN_APPROVAL','Admin Approval',2,true,'COORDINATION_MODE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COORDINATION_MODE','CONSENSUS','Consensus',3,true,'COORDINATION_MODE'),
																('COMMUNITY_COORDINATION','ALL','SETUP','COORDINATION_MODE','MIXED','Mixed',4,true,'COORDINATION_MODE'),
																
																('COMMUNITY_COORDINATION','ALL','ISSUE','CATEGORY','MAINTENANCE','Maintenance',1,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','ISSUE','CATEGORY','SECURITY','Security',2,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','ISSUE','CATEGORY','EVENT','Event',3,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','ISSUE','CATEGORY','REQUEST','Request',4,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','EVENT','CATEGORY','MEETING','Meeting',1,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','EVENT','CATEGORY','FESTIVAL','Festival',2,true,'WORK_ITEM_TYPE'),
																('COMMUNITY_COORDINATION','ALL','EVENT','CATEGORY','CAMPAIGN','Campaign',3,true,'WORK_ITEM_TYPE');
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category, value_group)
																VALUES
																('GROUP_LIFE','ALL','LIFE','DIMENSION','EXPERIENCE','Experience',1,true,'LIFE_MOMENT_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','DIMENSION','PURCHASE','Purchase',2,true,'LIFE_MOMENT_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','DIMENSION','LIVING','Living',3,true,'LIFE_MOMENT_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','DIMENSION','GOAL','Goal',4,true,'LIFE_MOMENT_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','DIMENSION','COMMUNITY','Community',5,true,'LIFE_MOMENT_DIMENSION'),
																
																('GROUP_LIFE','ALL','LIFE','BALANCE_DIMENSION','PARTICIPATION','Participation',1,true,'LIFE_BALANCE_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','BALANCE_DIMENSION','CONTRIBUTION','Contribution',2,true,'LIFE_BALANCE_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','BALANCE_DIMENSION','COORDINATION','Coordination',3,true,'LIFE_BALANCE_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','BALANCE_DIMENSION','PROGRESS','Progress',4,true,'LIFE_BALANCE_DIMENSION'),
																('GROUP_LIFE','ALL','LIFE','BALANCE_DIMENSION','COMMUNITY','Community',5,true,'LIFE_BALANCE_DIMENSION');
-- >>>STMT<<<
INSERT INTO group_field_value_config
																(moment_type, moment_profile, module_code, field_name, value_code, value_label, display_order, is_top_category, value_group)
																VALUES
																('SHARED_EXPERIENCE','ALL','ASSET','ASSET_CATEGORY','TRAVEL_DOC','Travel Document',1,true,'ASSET_CATEGORY'),
																('SHARED_EXPERIENCE','ALL','ASSET','ASSET_CATEGORY','TICKET','Ticket',2,true,'ASSET_CATEGORY'),
																('SHARED_EXPERIENCE','ALL','ASSET','ASSET_CATEGORY','BOOKING_VOUCHER','Booking Voucher',3,true,'ASSET_CATEGORY'),
																('SHARED_EXPERIENCE','ALL','ASSET','ASSET_CATEGORY','RECEIPT','Receipt',4,true,'ASSET_CATEGORY'),
																('SHARED_EXPERIENCE','ALL','ASSET','ASSET_CATEGORY','INVOICE','Invoice',5,true,'ASSET_CATEGORY'),
																('SHARED_PURCHASE','ALL','ASSET','ASSET_CATEGORY','INVOICE','Invoice',1,true,'ASSET_CATEGORY'),
																('SHARED_PURCHASE','ALL','ASSET','ASSET_CATEGORY','RECEIPT','Receipt',2,true,'ASSET_CATEGORY'),
																('SHARED_PURCHASE','ALL','ASSET','ASSET_CATEGORY','WARRANTY','Warranty',3,true,'ASSET_CATEGORY'),
																('SHARED_PURCHASE','ALL','ASSET','ASSET_CATEGORY','OWNERSHIP_DOC','Ownership Document',4,true,'ASSET_CATEGORY'),
																('SHARED_LIVING','ALL','ASSET','ASSET_CATEGORY','LEASE_AGREEMENT','Lease Agreement',1,true,'ASSET_CATEGORY'),
																('SHARED_LIVING','ALL','ASSET','ASSET_CATEGORY','UTILITY_BILL','Utility Bill',2,true,'ASSET_CATEGORY'),
																('SHARED_LIVING','ALL','ASSET','ASSET_CATEGORY','MAINTENANCE_RECEIPT','Maintenance Receipt',3,true,'ASSET_CATEGORY'),
																('SHARED_GOAL','ALL','ASSET','ASSET_CATEGORY','GOAL_DOC','Goal Document',1,true,'ASSET_CATEGORY'),
																('SHARED_GOAL','ALL','ASSET','ASSET_CATEGORY','PROGRESS_PROOF','Progress Proof',2,true,'ASSET_CATEGORY'),
																('COMMUNITY_COORDINATION','ALL','ASSET','ASSET_CATEGORY','NOTICE','Notice',1,true,'ASSET_CATEGORY'),
																('COMMUNITY_COORDINATION','ALL','ASSET','ASSET_CATEGORY','PERMIT','Permit',2,true,'ASSET_CATEGORY'),
																('COMMUNITY_COORDINATION','ALL','ASSET','ASSET_CATEGORY','EVENT_DOC','Event Document',3,true,'ASSET_CATEGORY');
-- >>>STMT<<<
UPDATE business_moment_members
																SET
																    can_add_runway_transactions =
																        role IN (
																            'Runway Owner',
																            'Finance Lead',
																            'Operations Lead',
																            'Financial Contributor'
																        ),
																    can_edit_financial_entries =
																        role IN (
																            'Runway Owner',
																            'Finance Lead'
																        ),
																    can_manage_runway_settings =
																        role = 'Runway Owner',
																    can_approve_runway_changes =
																        role IN (
																            'Runway Owner',
																            'Finance Lead',
																            'Approver'
																        );
-- >>>STMT<<<
UPDATE business_moment_members
																SET
																    can_add_operations_records =
																        role IN (
																            'Operations Owner',
																            'Operations Lead',
																            'Budget Controller',
																            'Contributor'
																        ),
																
																    can_edit_operations_records =
																        role IN (
																            'Operations Owner',
																            'Operations Lead'
																        ),
																
																    can_edit_own_operations_records =
																        role = 'Contributor',
																
																    can_approve_operations_requests =
																        role IN (
																            'Operations Owner',
																            'Approver'
																        ),
																
																    can_delete_operations_records =
																        role = 'Operations Owner',
																
																    can_manage_operations_settings =
																        role = 'Operations Owner';
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry (
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'team_operations',
'participation',
'Participation',
25,
'team_activities',
'activity_status',
'completed activities / assigned activities * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry (
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'team_operations',
'approval_efficiency',
'Approval Efficiency',
25,
'team_approval_requests',
'approval_status',
'approved requests within SLA / total approvals * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry (
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'team_operations',
'issue_resolution',
'Issue Resolution',
25,
'team_issue_risks',
'status',
'resolved issues / total issues * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry (
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'team_operations',
'execution_discipline',
'Execution Discipline',
25,
'team_updates',
'update_status',
'on-time updates / expected updates * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_runway',
'cash_position',
'Cash Position',
30,
'runway_cash_inflows',
'amount',
'current cash available / target runway reserve * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_runway',
'burn_stability',
'Burn Stability',
25,
'runway_expense_burns',
'amount',
'budgeted burn vs actual burn stability score'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_runway',
'forecast_accuracy',
'Forecast Accuracy',
25,
'runway_financial_updates',
'forecast_amount',
'forecast variance score'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_runway',
'revenue_momentum',
'Revenue Momentum',
20,
'runway_cash_inflows',
'amount',
'rolling 90-day revenue trend score'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_operations',
'operational_discipline',
'Operational Discipline',
30,
'operations_spend_entries',
'entry_date',
'logged activities completed on time / total activities * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_operations',
'issue_resolution',
'Issue Resolution',
25,
'operations_issues',
'issue_status',
'resolved issues / total issues * 100'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_operations',
'approval_velocity',
'Approval Velocity',
25,
'operations_approval_requests',
'approval_status',
'avg approval turnaround time score'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(
moment_type,
driver_code,
driver_name,
driver_weight,
source_table,
source_column,
formula_description
)
VALUES
(
'business_operations',
'process_improvement',
'Process Improvement',
20,
'operations_improvements',
'improvement_status',
'implemented improvements / proposed improvements * 100'
);
-- >>>STMT<<<
UPDATE business_driver_formula_registry
SET active_flag = FALSE
WHERE moment_type IN (
    'team_operations',
    'business_runway',
    'business_operations'
);
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(moment_type, driver_code, driver_name, driver_weight, source_table, source_column, formula_description)
VALUES
('team_operations', 'participation', 'Participation', 25, 'team_activities', 'activity_status', 'completed activities / total active activities * 100'),

('team_operations', 'approval_efficiency', 'Approval Efficiency', 25, 'team_approval_requests', 'approval_status', 'approved or resolved approvals / total approval requests * 100'),

('team_operations', 'issue_resolution', 'Issue Resolution', 25, 'team_issue_risks', 'resolution_status', 'resolved issues / total active issues * 100'),

('team_operations', 'execution_discipline', 'Execution Discipline', 25, 'team_activities', 'activity_status', 'completed + in_progress activities compared with planned workload');
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(moment_type, driver_code, driver_name, driver_weight, source_table, source_column, formula_description)
VALUES
('business_runway', 'cash_position', 'Cash Position', 30, 'business_runway_snapshots', 'cash_available', 'cash_available compared with required runway reserve'),

('business_runway', 'burn_stability', 'Burn Stability', 25, 'business_runway_snapshots', 'net_burn', 'lower and stable net burn improves score'),

('business_runway', 'forecast_accuracy', 'Forecast Accuracy', 25, 'runway_financial_updates', 'applied_status', 'stable financial updates and fewer assumption changes improve score'),

('business_runway', 'revenue_momentum', 'Revenue Momentum', 20, 'runway_cash_inflows', 'amount_in_operating_currency', 'recent revenue inflow trend compared with previous period');
-- >>>STMT<<<
INSERT INTO business_driver_formula_registry
(moment_type, driver_code, driver_name, driver_weight, source_table, source_column, formula_description)
VALUES
('business_operations', 'operational_discipline', 'Operational Discipline', 30, 'business_operations_snapshots', 'operations_health_status', 'healthy operations state, budget control, and issue discipline'),

('business_operations', 'issue_resolution', 'Issue Resolution', 25, 'operations_issues', 'issue_status', 'resolved issues / total active issues * 100'),

('business_operations', 'approval_velocity', 'Approval Velocity', 25, 'operations_approval_requests', 'approval_status', 'approved or completed approvals / total approval requests * 100'),

('business_operations', 'process_improvement', 'Process Improvement', 20, 'operations_improvements', 'improvement_status', 'completed improvements / total improvements * 100');

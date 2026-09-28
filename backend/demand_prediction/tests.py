from django.test import SimpleTestCase
from demand_prediction.engine import DecisionTreeEngine

class DemandPredictionEngineTest(SimpleTestCase):
    databases = {'default'}

    def test_run_pipeline(self):
        results = DecisionTreeEngine.run_pipeline()
        self.assertTrue(results.get('success'))
        self.assertIn('metadata', results)
        self.assertIn('summary', results)
        self.assertIn('entropy', results)
        self.assertIn('information_gains', results)
        self.assertIn('best_split', results)
        self.assertIn('decision_tree', results)
        self.assertIn('product_predictions', results)
        
        predictions = results['product_predictions']
        self.assertGreater(len(predictions), 0)
        
        self.assertIn('notify_me_count', DecisionTreeEngine.FEATURE_NAMES)
        self.assertIn('notify_me_count', results['information_gains'])

        sample = predictions[0]
        self.assertIn('product_key', sample)
        self.assertIn('product_name', sample)
        self.assertIn('latest_units_sold', sample)
        self.assertIn('latest_notify_me_count', sample)
        self.assertIn('notify_me_count', sample)
        self.assertIn('next_forecast_period', sample)
        self.assertIn('predicted_demand', sample)
        self.assertIn(sample['predicted_demand'], ['High', 'Medium', 'Low'])

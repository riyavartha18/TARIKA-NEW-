import math
from django.db import connection


class DecisionTreeEngine:
    """
    Pure Python Manual Implementation of Decision Tree Classifier for Demand Prediction.
    Strictly avoids sklearn or external ML libraries.

    Mathematical Workflow:
    1. Historical Demand Classification -> Target creation (High, Medium, Low)
    2. Entropy Calculation -> H(S) = - sum(p_i * log2(p_i))
    3. Information Gain Calculation -> IG(S, F, T) = H(S) - H_split(S, F, T)
    4. Best Split Selection -> Feature & Threshold maximizing IG
    5. Recursive Tree Construction
    6. Product Demand Prediction
    """

    FEATURE_NAMES = ['units_sold', 'cart_quantity', 'wishlist_count', 'discount_percentage']

    @staticmethod
    def calculate_entropy(targets):
        """
        Calculates Shannon Entropy H(S) for a list of target class labels.
        H(S) = - sum(p_i * log2(p_i))
        """
        if not targets:
            return 0.0
        
        n = len(targets)
        counts = {}
        for label in targets:
            counts[label] = counts.get(label, 0) + 1
        
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        
        return round(entropy, 4)

    @classmethod
    def calculate_split_gain(cls, dataset, feature, threshold, parent_entropy):
        """
        Calculates Information Gain for a candidate split (feature <= threshold).
        """
        n_total = len(dataset)
        if n_total == 0:
            return 0.0, [], []

        left_samples = [d for d in dataset if d[feature] <= threshold]
        right_samples = [d for d in dataset if d[feature] > threshold]

        if not left_samples or not right_samples:
            return 0.0, left_samples, right_samples

        left_targets = [d['target'] for d in left_samples]
        right_targets = [d['target'] for d in right_samples]

        entropy_left = cls.calculate_entropy(left_targets)
        entropy_right = cls.calculate_entropy(right_targets)

        weighted_entropy = (len(left_samples) / n_total) * entropy_left + (len(right_samples) / n_total) * entropy_right
        information_gain = parent_entropy - weighted_entropy

        return round(information_gain, 4), left_samples, right_samples

    @classmethod
    def evaluate_feature_gains(cls, dataset, parent_entropy):
        """
        Calculates the maximum Information Gain and optimal threshold for EACH feature at a given node.
        Used for reporting root feature importance.
        """
        feature_report = {}

        for feat in cls.FEATURE_NAMES:
            values = sorted(list(set([d[feat] for d in dataset])))
            best_gain = 0.0
            best_threshold = None

            if len(values) > 1:
                # Generate candidate thresholds (midpoints between consecutive distinct values)
                candidates = [(values[i] + values[i + 1]) / 2.0 for i in range(len(values) - 1)]
                # If too many candidate thresholds, subsample evenly up to 50 for efficiency
                if len(candidates) > 50:
                    step = len(candidates) // 50
                    candidates = candidates[::step]
            elif len(values) == 1:
                candidates = [values[0]]
            else:
                candidates = []

            for t in candidates:
                gain, left, right = cls.calculate_split_gain(dataset, feat, t, parent_entropy)
                if gain > best_gain:
                    best_gain = gain
                    best_threshold = t

            feature_report[feat] = {
                'gain': round(best_gain, 4),
                'best_threshold': round(best_threshold, 4) if best_threshold is not None else (round(values[0], 4) if values else 0.0),
                'feature_label': feat.replace('_', ' ').title()
            }

        # Sort feature report by Information Gain descending
        sorted_gains = dict(sorted(feature_report.items(), key=lambda item: item[1]['gain'], reverse=True))
        rank = 1
        for k in sorted_gains:
            sorted_gains[k]['rank'] = rank
            rank += 1

        return sorted_gains

    @classmethod
    def find_best_split(cls, dataset, parent_entropy):
        """
        Finds the single best feature and threshold split across all candidate features.
        """
        best_gain = -1.0
        best_feature = None
        best_threshold = None
        best_left = []
        best_right = []

        for feat in cls.FEATURE_NAMES:
            values = sorted(list(set([d[feat] for d in dataset])))
            if len(values) <= 1:
                continue

            candidates = [(values[i] + values[i + 1]) / 2.0 for i in range(len(values) - 1)]
            if len(candidates) > 50:
                step = len(candidates) // 50
                candidates = candidates[::step]

            for t in candidates:
                gain, left, right = cls.calculate_split_gain(dataset, feat, t, parent_entropy)
                if gain > best_gain and left and right:
                    best_gain = gain
                    best_feature = feat
                    best_threshold = t
                    best_left = left
                    best_right = right

        return {
            'feature': best_feature,
            'threshold': round(best_threshold, 4) if best_threshold is not None else None,
            'information_gain': round(max(best_gain, 0.0), 4),
            'left': best_left,
            'right': best_right
        }

    @classmethod
    def build_tree(cls, dataset, depth=0, max_depth=3, node_counter=None):
        """
        Recursively constructs the Decision Tree.
        """
        if node_counter is None:
            node_counter = [0]

        node_id = f"node_{node_counter[0]}"
        node_counter[0] += 1

        targets = [d['target'] for d in dataset]
        n_samples = len(dataset)

        # Count occurrences of class labels
        value_counts = {
            'High': targets.count('High'),
            'Medium': targets.count('Medium'),
            'Low': targets.count('Low')
        }

        # Majority class prediction
        prediction = max(value_counts, key=value_counts.get) if n_samples > 0 else 'Medium'
        node_entropy = cls.calculate_entropy(targets)

        # Check stopping criteria: pure node, max depth reached, or insufficient samples
        if node_entropy == 0.0 or depth >= max_depth or n_samples < 5:
            return {
                'node_id': node_id,
                'is_leaf': True,
                'prediction': prediction,
                'entropy': node_entropy,
                'samples': n_samples,
                'value_counts': value_counts,
                'depth': depth
            }

        split = cls.find_best_split(dataset, node_entropy)

        # If no valid split found or gain is zero
        if not split['feature'] or split['information_gain'] <= 0.0001 or not split['left'] or not split['right']:
            return {
                'node_id': node_id,
                'is_leaf': True,
                'prediction': prediction,
                'entropy': node_entropy,
                'samples': n_samples,
                'value_counts': value_counts,
                'depth': depth
            }

        left_node = cls.build_tree(split['left'], depth + 1, max_depth, node_counter)
        right_node = cls.build_tree(split['right'], depth + 1, max_depth, node_counter)

        return {
            'node_id': node_id,
            'is_leaf': False,
            'feature': split['feature'],
            'feature_label': split['feature'].replace('_', ' ').title(),
            'threshold': split['threshold'],
            'gain': split['information_gain'],
            'entropy': node_entropy,
            'samples': n_samples,
            'value_counts': value_counts,
            'prediction': prediction,
            'depth': depth,
            'left': left_node,
            'right': right_node
        }

    @classmethod
    def predict_sample(cls, node, sample):
        """
        Traverses Decision Tree to predict demand category for a given sample.
        """
        if node.get('is_leaf'):
            return node.get('prediction', 'Medium')

        feat = node['feature']
        thresh = node['threshold']

        if sample.get(feat, 0) <= thresh:
            return cls.predict_sample(node['left'], sample)
        else:
            return cls.predict_sample(node['right'], sample)

    @classmethod
    def run_pipeline(cls):
        """
        Fetches historical data from fact_demand, trains manual Decision Tree,
        and generates product-wise demand predictions along with mathematical metrics.
        """
        cursor = connection.cursor()
        
        # 1. Fetch historical demand dataset joined with product and category dimensions
        query = """
            SELECT 
                fd.product_key,
                COALESCE(dp.product_name, CONCAT('Product #', fd.product_key)) as product_name,
                COALESCE(dc.category_name, 'General Catalog') as category_name,
                AVG(fd.units_sold) as avg_units_sold,
                AVG(fd.cart_quantity) as avg_cart_qty,
                AVG(fd.wishlist_count) as avg_wishlist,
                AVG(fd.discount_percentage) as avg_discount,
                COUNT(fd.demand_key) as observation_count
            FROM fact_demand fd
            LEFT JOIN dim_product dp ON fd.product_key = dp.product_key
            LEFT JOIN dim_category dc ON fd.category_key = dc.category_key
            GROUP BY fd.product_key, dp.product_name, dc.category_name
            ORDER BY fd.product_key ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return {
                'success': False,
                'error': 'No historical records found in fact_demand table.'
            }

        # 2. Extract product dataset records
        dataset = []
        for r in rows:
            dataset.append({
                'product_key': r[0],
                'product_name': r[1],
                'category_name': r[2],
                'units_sold': float(r[3] or 0),
                'cart_quantity': float(r[4] or 0),
                'wishlist_count': float(r[5] or 0),
                'discount_percentage': float(r[6] or 0),
                'observations': int(r[7] or 1)
            })

        # 3. Create target demand categories (High, Medium, Low) based on historical units_sold percentiles
        units_values = sorted([d['units_sold'] for d in dataset])
        n_units = len(units_values)
        p33 = units_values[n_units // 3]
        p66 = units_values[(2 * n_units) // 3]

        for d in dataset:
            if d['units_sold'] <= p33:
                d['target'] = 'Low'
            elif d['units_sold'] <= p66:
                d['target'] = 'Medium'
            else:
                d['target'] = 'High'

        targets = [d['target'] for d in dataset]
        total_products = len(dataset)

        # 4. Calculate Root Entropy
        root_entropy = cls.calculate_entropy(targets)

        # 5. Calculate Information Gain for EACH feature at Root
        feature_gains = cls.calculate_feature_gains_report(dataset, root_entropy)

        # 6. Determine Best Split at Root
        best_split_info = cls.find_best_split(dataset, root_entropy)
        
        best_split_summary = {
            'feature': best_split_info['feature'],
            'feature_label': best_split_info['feature'].replace('_', ' ').title() if best_split_info['feature'] else 'N/A',
            'threshold': best_split_info['threshold'],
            'information_gain': best_split_info['information_gain'],
            'explanation': f"The optimal root split is on '{best_split_info['feature'].replace('_', ' ').title()}' at threshold <= {best_split_info['threshold']}, yielding the maximum Information Gain of {best_split_info['information_gain']} bits." if best_split_info['feature'] else "No valid split found."
        }

        # 7. Construct Manual Decision Tree
        decision_tree = cls.build_tree(dataset, depth=0, max_depth=3)

        # 8. Generate Product-Wise Predicted Demand
        product_predictions = []
        high_count = 0
        med_count = 0
        low_count = 0

        for d in dataset:
            pred_demand = cls.predict_sample(decision_tree, d)
            if pred_demand == 'High':
                high_count += 1
            elif pred_demand == 'Medium':
                med_count += 1
            else:
                low_count += 1

            product_predictions.append({
                'product_key': d['product_key'],
                'product_name': d['product_name'],
                'category_name': d['category_name'],
                'units_sold': round(d['units_sold'], 2),
                'cart_quantity': round(d['cart_quantity'], 2),
                'wishlist_count': round(d['wishlist_count'], 2),
                'discount_percentage': round(d['discount_percentage'], 2),
                'actual_demand': d['target'],
                'predicted_demand': pred_demand,
                'is_match': d['target'] == pred_demand
            })

        # Calculate accuracy score
        matches = sum(1 for p in product_predictions if p['is_match'])
        accuracy_percentage = round((matches / total_products) * 100, 2) if total_products > 0 else 100.0

        # Also get total row count from fact_demand for metadata
        cursor.execute("SELECT COUNT(*) FROM fact_demand")
        fact_demand_total_rows = cursor.fetchone()[0]

        return {
            'success': True,
            'metadata': {
                'module_name': 'Demand Forecasting & Prediction',
                'algorithm': 'Manual Decision Tree Classifier (Entropy & Information Gain)',
                'total_historical_rows': fact_demand_total_rows,
                'total_products_analyzed': total_products,
                'accuracy_percentage': accuracy_percentage
            },
            'summary': {
                'total_products': total_products,
                'root_entropy': root_entropy,
                'demand_cutoffs': {
                    'low_max': round(p33, 2),
                    'medium_max': round(p66, 2)
                },
                'predicted_distribution': {
                    'High': high_count,
                    'Medium': med_count,
                    'Low': low_count
                },
                'actual_distribution': {
                    'High': targets.count('High'),
                    'Medium': targets.count('Medium'),
                    'Low': targets.count('Low')
                }
            },
            'entropy': {
                'root_entropy': root_entropy,
                'formula': 'H(S) = - sum( p_i * log2(p_i) )',
                'description': f"Root dataset entropy is {root_entropy} bits across 3 target demand classes (High, Medium, Low)."
            },
            'information_gains': feature_gains,
            'best_split': best_split_summary,
            'decision_tree': decision_tree,
            'product_predictions': product_predictions
        }

    @classmethod
    def calculate_feature_gains_report(cls, dataset, root_entropy):
        return cls.evaluate_feature_gains(dataset, root_entropy)

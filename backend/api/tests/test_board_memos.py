# pyright: reportAttributeAccessIssue=false

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from api.models import BoardMemo

from .base import ApiTestCase


class BoardMemoApiTests(ApiTestCase):
    def test_list_returns_unarchived_current_shop_memos_even_when_created_before_today(self):
        self.login_owner()
        active = BoardMemo.objects.create(shop=self.shop, text="玉ねぎ")
        BoardMemo.objects.filter(id=active.id).update(
            created_at=timezone.now() - timedelta(days=2)
        )
        active.refresh_from_db()
        BoardMemo.objects.create(shop=self.other_shop, text="別店舗メモ")

        response = self.client.get(reverse("board-memo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [active.id])
        self.assertFalse(response.data[0]["is_archived"])

    def test_list_returns_today_archived_memos_after_unarchived_memos(self):
        self.login_owner()
        active = BoardMemo.objects.create(shop=self.shop, text="玉ねぎ")
        archived = BoardMemo.objects.create(
            shop=self.shop,
            text="ラップ",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("board-memo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [active.id, archived.id])
        self.assertFalse(response.data[0]["is_archived"])
        self.assertTrue(response.data[1]["is_archived"])

    def test_list_excludes_memos_archived_before_today(self):
        self.login_owner()
        archived = BoardMemo.objects.create(
            shop=self.shop,
            text="昨日のメモ",
            archived_at=timezone.now() - timedelta(days=1),
        )

        response = self.client.get(reverse("board-memo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(archived.id, [item["id"] for item in response.data])

    def test_list_can_include_archived_for_history_candidates(self):
        self.login_owner()
        active = BoardMemo.objects.create(shop=self.shop, text="玉ねぎ")
        archived = BoardMemo.objects.create(
            shop=self.shop,
            text="フライヤー油交換",
            archived_at=timezone.now() - timedelta(days=3),
        )

        response = self.client.get(reverse("board-memo-list"), {"include_archived": "1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual([item["id"] for item in response.data], [active.id, archived.id])

    def test_create_board_memo_sets_current_shop(self):
        self.login_owner()

        response = self.client.post(
            reverse("board-memo-list"),
            {"text": " ラップ補充 ", "shop": self.other_shop.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        memo = BoardMemo.objects.get(id=response.data["id"])
        self.assertEqual(memo.shop, self.shop)
        self.assertEqual(memo.text, "ラップ補充")

    def test_staff_can_create_board_memo(self):
        self.login_staff()

        response = self.client.post(
            reverse("board-memo-list"),
            {"text": "ラップ補充"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        memo = BoardMemo.objects.get(id=response.data["id"])
        self.assertEqual(memo.shop, self.shop)
        self.assertEqual(memo.text, "ラップ補充")

    def test_create_board_memo_rejects_blank_text(self):
        self.login_owner()

        response = self.client.post(
            reverse("board-memo-list"),
            {"text": "  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)

    def test_archive_board_memo_sets_archived_at_and_keeps_it_in_today_list(self):
        self.login_owner()
        memo = BoardMemo.objects.create(shop=self.shop, text="玉ねぎ")

        archive_response = self.client.patch(reverse("board-memo-archive", args=[memo.id]))
        list_response = self.client.get(reverse("board-memo-list"))

        self.assertEqual(archive_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(archive_response.data["archived_at"])
        self.assertTrue(archive_response.data["is_archived"])
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in list_response.data], [memo.id])
        self.assertTrue(list_response.data[0]["is_archived"])

    def test_staff_can_archive_board_memo(self):
        self.login_staff()
        memo = BoardMemo.objects.create(shop=self.shop, text="玉ねぎ")

        response = self.client.patch(reverse("board-memo-archive", args=[memo.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        memo.refresh_from_db()
        self.assertIsNotNone(memo.archived_at)

    def test_staff_can_unarchive_board_memo(self):
        self.login_staff()
        memo = BoardMemo.objects.create(
            shop=self.shop,
            text="玉ねぎ",
            archived_at=timezone.now(),
        )

        response = self.client.patch(reverse("board-memo-unarchive", args=[memo.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        memo.refresh_from_db()
        self.assertIsNone(memo.archived_at)

    def test_unarchive_board_memo_returns_it_to_unchecked(self):
        self.login_owner()
        memo = BoardMemo.objects.create(
            shop=self.shop,
            text="玉ねぎ",
            archived_at=timezone.now(),
        )

        unarchive_response = self.client.patch(reverse("board-memo-unarchive", args=[memo.id]))
        list_response = self.client.get(reverse("board-memo-list"))

        self.assertEqual(unarchive_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(unarchive_response.data["archived_at"])
        self.assertFalse(unarchive_response.data["is_archived"])
        self.assertEqual([item["id"] for item in list_response.data], [memo.id])
        self.assertFalse(list_response.data[0]["is_archived"])

    def test_cannot_archive_other_shop_board_memo(self):
        self.login_owner()
        memo = BoardMemo.objects.create(shop=self.other_shop, text="秘密メモ")

        response = self.client.patch(reverse("board-memo-archive", args=[memo.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        memo.refresh_from_db()
        self.assertIsNone(memo.archived_at)

    def test_cannot_unarchive_other_shop_board_memo(self):
        self.login_owner()
        memo = BoardMemo.objects.create(
            shop=self.other_shop,
            text="秘密メモ",
            archived_at=timezone.now(),
        )

        response = self.client.patch(reverse("board-memo-unarchive", args=[memo.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        memo.refresh_from_db()
        self.assertIsNotNone(memo.archived_at)
